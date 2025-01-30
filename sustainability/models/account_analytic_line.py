from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    carbon_currency_id = fields.Many2one(
        "res.currency",
        related="move_line_id.carbon_currency_id",
    )
    carbon_debt = fields.Monetary(
        string="CO2",
        currency_field="carbon_currency_id",
    )

    @api.model
    def _get_carbon_fields_custom_group(self):
        return "account.group_account_invoice"
