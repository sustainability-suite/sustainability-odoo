from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    # Legacy
    carbon_currency_id = fields.Many2one(
        'res.currency',
        compute="_compute_carbon_currency_id",
    )

    def _compute_carbon_currency_id(self):
        for analytic_account in self:
            analytic_account.carbon_currency_id = self.env.ref("onsp_co2.carbon_kilo", raise_if_not_found=False)
