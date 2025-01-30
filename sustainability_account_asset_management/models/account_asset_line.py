from odoo import api, models


class AccountAssetLine(models.Model):
    _inherit = "account.asset.line"

    def create_move(self):
        res = super().create_move()
        self.env["account.move"].browse(res).line_ids._compute_carbon_debt(
            force_compute="all_states"
        )
        return res

    @api.model
    def _get_carbon_fields_custom_group(self):
        return "account.group_account_invoice"
