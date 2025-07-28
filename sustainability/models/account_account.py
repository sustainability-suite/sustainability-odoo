from odoo import api, fields, models


class AccountAccount(models.Model):
    _name = "account.account"
    _inherit = ["account.account", "carbon.mixin", "carbon.common.mixin"]
    _carbon_types = ["in"]

    @api.model
    def _get_available_carbon_compute_methods(self) -> list[tuple[str, str]]:
        return [
            ("monetary", "Monetary"),
        ]

    carbon_in_factor_id = fields.Many2one(
        string="Emission Factor Purchases", tracking=True
    )

    carbon_line_origin_ids = fields.One2many(
        comodel_name="carbon.line.origin",
        inverse_name="move_line_account_id",
        string="Origins",
    )
    carbon_line_origin_qty = fields.Integer(compute="_compute_carbon_line_origin_qty")

    def action_see_carbon_line_origin_ids(self):
        return self._generate_action(
            model="carbon.line.origin",
            ids=self.carbon_line_origin_ids.ids,
        )

    def _compute_carbon_line_origin_qty(self):
        for factor in self:
            factor.carbon_line_origin_qty = len(factor.carbon_line_origin_ids)
