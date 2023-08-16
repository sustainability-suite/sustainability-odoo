from odoo import api, fields, models, _
from typing import Union


STATES_TO_AUTO_RECOMPUTE = ['draft']


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
    carbon_is_locked = fields.Boolean(default=False)

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
            credit = 0.0
            debit = 0.0
            # Weird if/elif statement, but we need that order of priority
            if line.move_id.is_inbound(include_receipts=True):
                credit = line.carbon_debt
            elif line.move_id.is_outbound(include_receipts=True):
                debit = line.carbon_debt
            elif line.credit != 0:
                credit = line.carbon_debt
            elif line.debit != 0:
                debit = line.carbon_debt

            line.carbon_credit = credit
            line.carbon_debit = debit

    def _filter_lines_to_compute(self, force_compute: Union[bool, str, list[str]] = None):
        if force_compute is None:
            force_compute = []
        elif isinstance(force_compute, bool):
            force_compute = ['posted', 'locked'] if force_compute else []
        elif isinstance(force_compute, str):
            force_compute = [force_compute]

        # if 'posted' not in force_compute:
        #     lines = lines.filtered(lambda l: l.move_id.state in STATES_TO_AUTO_RECOMPUTE)
        # if 'locked' not in force_compute:
        #     lines = lines.filtered(lambda l: not l.carbon_is_locked)

        # TODO ASAP: Make it a SQL query because this is fucking ugly
        res = self.env['account.move.line']
        for line in self:
            if (
                    ('posted' not in force_compute and line.move_id.state not in STATES_TO_AUTO_RECOMPUTE)
                    or ('locked' not in force_compute and line.carbon_is_locked)
                    or (line.move_id.company_id.carbon_lock_date and line.move_id.date < line.move_id.company_id.carbon_lock_date)
            ):
                continue
            res |= line

        return res

    @api.depends(
        'account_id.use_carbon_value',
        'account_id.carbon_in_value',
        'account_id.carbon_in_compute_method',
        'account_id.carbon_in_uom_id',
        'account_id.carbon_in_monetary_currency_id',

        'product_id.carbon_in_value',
        'product_id.carbon_in_compute_method',
        'product_id.carbon_in_uom_id',
        'product_id.carbon_in_monetary_currency_id',

        'product_id.carbon_out_value',
        'product_id.carbon_out_compute_method',
        'product_id.carbon_out_uom_id',
        'product_id.carbon_out_monetary_currency_id',

        'quantity',
        'credit',
        'debit',
        'move_type',
        'move_id.invoice_date',
        'move_id.company_id.carbon_lock_date',
    )
    def _compute_carbon_debt(self, force_compute: Union[bool, str, list[str]] = None):
        lines_to_compute = self._filter_lines_to_compute(force_compute=force_compute)

        for line in lines_to_compute:
            amount = getattr(line, "debit" if line.is_debit() else "credit", 0.0)
            # We don't take discounts into account for carbon values, so we need to reverse it
            # There is a very special case if the discount is exactly 100% (division by 0) so we have to get a value somehow with price_unit*quantity
            if line.discount:
                amount = amount / (1 - line.discount / 100) if line.discount != 100 else line.price_unit * line.quantity

            # These are the common arguments for the carbon value computation
            # Others values are added below depending on the record type
            kw_arguments = {
                'carbon_type': 'out' if line.move_id.is_sale_document() else 'in',
                'date': line.move_id.date or line.move_id.invoice_date,
                'amount': amount,
                # We take the company currency because credit/debit are expressed in that currency
                'from_currency_id': (line.move_id.company_id or self.env.company).currency_id,
            }


            for field in line.get_possible_fields_to_compute_carbon():
                if getattr(line, f"can_use_{field}_carbon_value", lambda: False)():
                    record = getattr(line, field)
                    kw_arguments.update(getattr(line, f"get_{field}_carbon_compute_values", lambda: {})())
                    break
            else:
                record = line.move_id.company_id or self.env.company


            debt, infos = record.get_carbon_value(**kw_arguments)
            line.carbon_debt = debt
            line.carbon_value_origin = f"{infos['carbon_value_origin']}|{infos['carbon_value']}"


    # --------------------------------------------
    #                ACTION / UI
    # --------------------------------------------


    def action_see_carbon_origin(self):
        self.ensure_one()
        origin = {
            'name': _("No CO2e origin for this record"),
            'value': 0,
        }
        for key, data in zip(['name', 'value'], self.carbon_value_origin.split("|")):
            if data:
                origin[key] = data

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': f"CO2e Value: {origin.get('value')}",
                'message': origin.get('name'),
                'type': 'info',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def action_recompute_carbon(self) -> dict:
        """ Force re-computation of carbon values for lines. Todo: add a confirm dialog if a subset is 'posted' """
        for line in self:
            line._compute_carbon_debt(force_compute='posted')
        return {}

    def action_switch_locked(self):
        for line in self:
            line.carbon_is_locked = not line.carbon_is_locked

    # --------------------------------------------
    #                   MISC
    # --------------------------------------------


    def _prepare_analytic_distribution_line(self, distribution, account_id, distribution_on_each_plan) -> dict:
        """ I removed _prepare_analytic_line() (which is renamed in v16) because it calls this actual method to do the job """
        res = super(AccountMoveLine, self)._prepare_analytic_distribution_line(distribution, account_id, distribution_on_each_plan)
        res["carbon_debt"] = -self.carbon_debt * distribution / 100.0
        return res



    # --------------------------------------------
    #              Modular methods
    # --------------------------------------------


    @api.model
    def get_possible_fields_to_compute_carbon(self):
        return ['product_id', 'account_id']


    """ These methods are helper to know if a line has valid co2 values to compute line debt """
    # --- ACCOUNT ---
    def can_use_account_id_carbon_value(self) -> bool:
        self.ensure_one()
        return self.account_id.use_carbon_value and self.account_id.has_valid_carbon_in_value()

    def get_account_id_carbon_compute_values(self) -> dict:
        self.ensure_one()
        return {'carbon_type': 'in'}

    # --- PRODUCT ---
    def can_use_product_id_carbon_value(self) -> bool:
        self.ensure_one()
        return bool(self.product_id) and (
            (self.move_id.is_outbound(include_receipts=True) and self.product_id.has_valid_carbon_in_value()) or
            (self.move_id.is_inbound(include_receipts=True) and self.product_id.has_valid_carbon_out_value())
        )

    def get_product_id_carbon_compute_values(self) -> dict:
        self.ensure_one()
        return {'quantity': self.quantity, 'from_uom_id': self.product_uom_id}


    """ These methods might seem useless but the logic could change in the future so it's better to have them """
    def is_debit(self) -> bool:
        self.ensure_one()
        return bool(self.debit)

    def is_credit(self) -> bool:
        self.ensure_one()
        return bool(self.credit)
