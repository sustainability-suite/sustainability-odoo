from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    move_partner_id = fields.Many2one(
        related="move_id.partner_id", store=True, string="Invoice Partner"
    )

    @api.model
    def _get_carbon_compute_possible_fields(self) -> list[str]:
        res = super()._get_carbon_compute_possible_fields()
        res = ["partner_id", "move_partner_id"] + res
        return res

    # --- Partner ---
    def can_use_partner_id_carbon_value(self) -> bool:
        self.ensure_one()
        return self.move_id.is_outbound(include_receipts=True) and (
            self.partner_id and self.partner_id.can_compute_carbon_value("in")
        )

    # --- Move Partner ---
    def can_use_move_partner_id_carbon_value(self) -> bool:
        self.ensure_one()
        return self.move_id.is_outbound(include_receipts=True) and (
            self.move_partner_id and self.move_partner_id.can_compute_carbon_value("in")
        )

    @api.depends(
        "partner_id.carbon_in_factor_id", "move_partner_id.carbon_in_factor_id"
    )
    def _compute_carbon_debt(self, force_compute=None):
        return super()._compute_carbon_debt(force_compute)
