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
    # Todo: fix origin + general logic flow
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
        'product_id.carbon_value',
        'product_id.carbon_sale_value',
        'price_subtotal',
        'move_type',
    )
    def _compute_carbon_debt(self, force_compute: bool = False):
        lines = self if force_compute else self.filtered(lambda l: l.move_id.state == 'draft')
        for line in lines:
            debt = 0
            origin = ""
            if line.use_account_carbon_value():
                debt = line.price_subtotal * line.account_id.carbon_value
                origin = line.account_id.carbon_value_origin
            elif line.use_product_carbon_value():
                if line.move_id.is_inbound(include_receipts=True):
                    debt = line.product_id.get_carbon_value('credit', quantity=line.quantity, price=line.price_subtotal)
                    origin = line.product_id.carbon_sale_value_origin
                elif line.move_id.is_outbound(include_receipts=True):
                    debt = line.product_id.get_carbon_value('debit', quantity=line.quantity, price=line.price_subtotal)
                    origin = line.product_id.carbon_value_origin

            line.carbon_debt = debt
            line.carbon_value_origin = origin




    # --------------------------------------------
    #                ACTION / UI
    # --------------------------------------------


    def action_see_carbon_origin(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': f"CO2e Value: {self.carbon_value_origin or 'None'}",
                'message': self.carbon_value_origin or _("No CO2e origin for this record"),
                'type': 'info',
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
        # return super(AccountMoveLine, self).action_see_carbon_origin()




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
        return not self.product_id and self.account_id.use_carbon_value

    def use_product_carbon_value(self) -> bool:
        self.ensure_one()
        return bool(self.product_id)
