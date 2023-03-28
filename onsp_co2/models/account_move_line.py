from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    carbon_currency_id = fields.Many2one(related="move_id.carbon_currency_id")
    carbon_debt = fields.Monetary(
        string="CO2 Debt",
        currency_field="carbon_currency_id",
        help="A positive value means that your system's debt grows, a negative value means it shrinks",
        compute="_compute_carbon_debt",
        readonly=False,
        store=True,
    )
    carbon_value_origin = fields.Char(compute="_compute_carbon_debt", string="CO2e value origin", store=True)

    carbon_balance = fields.Monetary(
        string="CO2 Balance",
        currency_field="carbon_currency_id",
        compute="_compute_carbon_balance",
        store=True,
    )
    carbon_debit = fields.Monetary(
        string="CO2 Debit",
        currency_field="carbon_currency_id",
        compute="_compute_carbon_debit_credit",
        store=True,
    )
    carbon_credit = fields.Monetary(
        string="CO2 Credit",
        currency_field="carbon_currency_id",
        compute="_compute_carbon_debit_credit",
        store=True,
    )


    # --------------------------------------------
    #                   COMPUTE
    # --------------------------------------------


    @api.depends("carbon_debit", "carbon_credit")
    def _compute_carbon_balance(self):
        for line in self:
            line.carbon_balance = line.carbon_debit - line.carbon_credit

    @api.depends('carbon_debt', 'credit', 'debit')
    def _compute_carbon_debit_credit(self):
        for line in self:
            if line.move_id.is_inbound(include_receipts=True):
                line.carbon_credit = line.carbon_debt
                line.carbon_debit = 0
            elif line.move_id.is_outbound(include_receipts=True):
                line.carbon_credit = 0
                line.carbon_debit = line.carbon_debt


    @api.depends(
        'account_id.use_carbon_value',
        'account_id.carbon_value',
        'account_id.carbon_compute_method',
        'account_id.carbon_uom_id',
        'account_id.carbon_monetary_currency_id',

        'product_id.carbon_value',
        'product_id.carbon_compute_method',
        'product_id.carbon_uom_id',
        'product_id.carbon_monetary_currency_id',

        'product_id.carbon_sale_value',
        'product_id.carbon_compute_method',
        'product_id.carbon_uom_id',
        'product_id.carbon_monetary_currency_id',

        'price_subtotal',
        'move_type',
    )
    def _compute_carbon_debt(self, force_compute: bool = False):
        lines = self if force_compute else self.filtered(lambda l: l.move_id.state == 'draft')
        for line in lines:
            debt = 0
            origin = ""

            if line.move_id.is_inbound(include_receipts=True):
                line_type = "credit"
            elif line.move_id.is_outbound(include_receipts=True):
                line_type = "debit"
            else:
                line.carbon_debt = debt
                line.carbon_value_origin = origin
                continue

            if line.use_product_carbon_value():
                debt, infos = line.product_id.get_carbon_value(line_type, quantity=line.quantity, price=line.price_subtotal)
                origin = line.product_id.carbon_sale_value_origin if line_type == 'credit' else line.product_id.carbon_value_origin
                origin += "|" + str(infos[0])
            elif line.use_account_carbon_value():
                value = getattr(line, line_type, 0.0)
                debt = value * line.account_id.carbon_value
                origin = line.account_id.carbon_value_origin + "|" + str(round(line.account_id.carbon_value, 4))
            else:
                company = line.move_id.company_id or self.env.company
                carbon_value = company.carbon_sale_value if line_type == 'credit' else company.carbon_value
                debt = line.price_subtotal * carbon_value
                origin = company.name + "|" + str(carbon_value)
            line.carbon_debt = debt
            line.carbon_value_origin = origin




    # --------------------------------------------
    #                ACTION / UI
    # --------------------------------------------


    def action_see_carbon_origin(self):
        self.ensure_one()
        origin, value = self.carbon_value_origin.split("|")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': f"CO2e Value: {value or 'None'}",
                'message': origin or _("No CO2e origin for this record"),
                'type': 'info',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def action_recompute_carbon(self):
        """ Force re-computation of carbon values for lines. Todo: add a confirm dialog if a subset is 'posted' """
        for line in self:
            line._compute_carbon_debt(force_compute=True)


    # --------------------------------------------
    #                   MISC
    # --------------------------------------------


    def _prepare_analytic_distribution_line(self, distribution, account_id, distribution_on_each_plan) -> dict:
        """
        To be tested functionally
        I removed _prepare_analytic_line() (which is renamed in v16) because it calls this actual method to do the job
        """
        res = super(AccountMoveLine, self)._prepare_analytic_distribution_line(distribution, account_id, distribution_on_each_plan)
        res["carbon_debt"] = -self.carbon_debt * distribution / 100.0
        return res

    def use_account_carbon_value(self) -> bool:
        self.ensure_one()
        return self.account_id.use_carbon_value and self.account_id.has_valid_carbon_value()

    def use_product_carbon_value(self) -> bool:
        self.ensure_one()
        return self.product_id and (
            (self.move_id.is_outbound(include_receipts=True) and self.product_id.has_valid_carbon_value()) or
            (self.move_id.is_inbound(include_receipts=True) and self.product_id.has_valid_carbon_sale_value())
        )
