from odoo import api, fields, models


class AccountAccount(models.Model):
    _name = "account.account"
    _inherit = ["account.account", "carbon.mixin"]
    _carbon_types = ["in"]

    @api.model
    def _get_available_carbon_compute_methods(self) -> list[tuple[str, str]]:
        return [
            ("monetary", "Monetary"),
        ]

    carbon_in_factor_id = fields.Many2one(
        string="Emission Factor Purchases", tracking=True
    )
