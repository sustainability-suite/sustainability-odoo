# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

class AccountAccount(models.Model):
    _inherit = 'account.account'

    ons_use_co2_ratio = fields.Boolean(
        string="Use CO2 Conversion Ratio",
    )

    ons_carbon_ratio = fields.Float(
        string="CO2 Conversion Ratio",
        digits=(10, 3),
        help="Used to compute the CO2 debt relatively to the product unit",
    )