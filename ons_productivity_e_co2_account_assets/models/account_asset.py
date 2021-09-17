# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _
from math import floor

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    # Complete override
    def compute_depreciation_board(self):
        res = super(AccountAsset, self).compute_depreciation_board()
        amount_total = sum(m.amount_total for m in self.depreciation_move_ids)
        co2_total = sum(m.ons_carbon_debt for m in self.original_move_line_ids) 
        if not amount_total or not co2_total:
            return res

        co2_ratio = co2_total / amount_total

        posted_depreciation_move_ids = self.depreciation_move_ids.filtered(
            lambda x: x.state == 'posted' and not x.asset_value_change and not x.reversal_move_id
        ).sorted(key=lambda l: l.date)
        # already_depreciated_amount = sum(m.amount_total for m in posted_depreciation_move_ids)
        todo = (self.depreciation_move_ids - posted_depreciation_move_ids)[::-1]
        co2_temp = 0
        for iteration, move in enumerate(todo):
            value_max = 0
            for line in move.line_ids:
                value = co2_ratio * (line.credit + line.debit)
                if value > value_max:
                    value_max = value
                line.ons_carbon_debt = value
                line._ons_co2_onchange_ons_carbon_debt()
            
            if iteration == self.method_number - 1:
                amount = co2_total - co2_temp

            else:
                rounding = 1 / move.ons_co2_currency_id.rounding
                # Design choice: We assume that one line will balance the co2 accounts, being the
                # sum of the other lines. It then makes sense to assume that the max of every line
                # is the correct value for the carbon debt deferred. We also use a mathematical way
                # to floor the result at two digits.
                amount = floor(value_max * rounding) / rounding
                co2_temp += amount
            
            move.ons_carbon_debt_deferred = amount
            

        return res