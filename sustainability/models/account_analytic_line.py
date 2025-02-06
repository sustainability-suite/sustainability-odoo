from odoo import fields, models


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
