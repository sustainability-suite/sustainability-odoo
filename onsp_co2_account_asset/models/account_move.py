from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _prepare_move_for_asset_depreciation(self, vals):
        res = super(AccountMove, self)._prepare_move_for_asset_depreciation(vals)

        """ This method should be called only in draft mode, so we will use original_value """
        asset = self.env['account.asset'].browse(res['asset_id'])
        total_carbon_debt = asset.carbon_debt
        total_amount = asset.original_value

        for dum, my, line_vals in res['line_ids']:
            carbon_value = total_carbon_debt * line_vals['amount_currency'] / total_amount
            sign = 1 if asset.account_depreciation_id.id == line_vals['account_id'] else -1
            line_vals.update({'carbon_debt': carbon_value * sign, 'carbon_is_locked': True})

        return res

