# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'


    ons_co2_asset_remaining_value = fields.Monetary(string='Depreciable CO2 Value', copy=False)
    ons_co2_asset_depreciated_value = fields.Monetary(string='Cumulative CO2 Depreciation', copy=False)

    ons_carbon_debt_deferred = fields.Monetary(
        string="CO2 Debt (Kg)",
        currency_field="ons_co2_currency_id",
    )