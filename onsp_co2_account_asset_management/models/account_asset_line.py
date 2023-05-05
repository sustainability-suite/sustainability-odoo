from odoo import models

class AccountAssetLine(models.Model):
    _inherit = "account.asset.line"

    def create_move(self):
        res = super(AccountAssetLine, self).create_move()
        self.env['account.move'].browse(res).line_ids._compute_carbon_debt(force_compute='posted')
        return res
