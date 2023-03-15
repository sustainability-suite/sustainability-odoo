from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    # Legacy
    carbon_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref("onsp_co2.carbon_kilo", None),
    )
