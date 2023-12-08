from odoo import api, fields, models, _
from typing import Union

class HrExpense(models.Model):
    _name = "hr.expense"
    _inherit = ["hr.expense", "carbon.line.mixin"]

    def is_debit(self) -> bool:
        self.ensure_one()
        return False

    def is_credit(self) -> bool:
        self.ensure_one()
        return True

    # --------------------------------------------
    #                   COMPUTE
    # --------------------------------------------

    @api.depends("carbon_debit", "carbon_credit")
    def _compute_carbon_balance(self):
        for line in self:
            line.carbon_balance = line.carbon_debit - line.carbon_credit

    @api.depends(
        'account_id.carbon_in_factor_id',
        'product_id.carbon_in_factor_id',

        'quantity',
        'total_amount',
        'date'
    )
    def _compute_carbon_debt(self, force_compute: Union[bool, str, list[str]] = None):
        super()._compute_carbon_debt(force_compute)


    @api.model
    def _get_states_to_auto_recompute(self) -> list[str]:
        return ['draft']

    @api.model
    def _get_state_field_name(self) -> str:
        return 'state'

    @api.model
    def _get_carbon_compute_possible_fields(self) -> list[str]:
        return ['product_id', 'account_id']

    def _get_carbon_compute_kwargs(self) -> dict:
        res = super()._get_carbon_compute_kwargs()
        res.update({
            'carbon_type': 'in',
            'date': self.date,
            'from_currency_id': (self.company_id or self.env.company).currency_id,
        })
        return res

    def _get_line_amount(self) -> float:
        self.ensure_one()
        return self.total_amount or 0.0

    def can_use_account_id_carbon_value(self) -> bool:
        self.ensure_one()
        return self.account_id.can_compute_carbon_value('in')

    def get_account_id_carbon_compute_values(self) -> dict:
        self.ensure_one()
        return {'carbon_type': 'in'}

    # --- PRODUCT ---
    def can_use_product_id_carbon_value(self) -> bool:
        self.ensure_one()
        return bool(self.product_id) and self.product_id.can_compute_carbon_value('in')

    def get_product_id_carbon_compute_values(self) -> dict:
        self.ensure_one()
        return {'quantity': self.quantity, 'from_uom_id': self.product_uom_id}

    # --------------------------------------------
    #                   MOVE
    # --------------------------------------------

    def _prepare_move_line_vals(self):
        self.ensure_one()
        res = super()._prepare_move_line_vals()
        res.update({
            'carbon_debt': self.carbon_debt,
            'carbon_is_locked': self.carbon_is_locked,
        })
        return res
