from odoo import api, models, fields

class AccountAsset(models.Model):
    _inherit = "account.asset"

    carbon_debt = fields.Float(compute="_compute_carbon_debt", string="CO2 Debt", store=True)
    carbon_currency_id = fields.Many2one(
        'res.currency',
        compute="_compute_carbon_currency_id",
    )

    def _compute_carbon_currency_id(self):
        for asset in self:
            asset.carbon_currency_id = self.env.ref("onsp_co2.carbon_kilo", raise_if_not_found=False)

    @api.depends('original_move_line_ids.carbon_debt')
    def _compute_carbon_debt(self):
        for asset in self:
            asset.carbon_debt = sum(asset.original_move_line_ids.mapped('carbon_debt'))


