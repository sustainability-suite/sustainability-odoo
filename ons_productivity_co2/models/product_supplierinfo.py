# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    ons_carbon_ratio = fields.Float(
        string="CO2 Conversion Ratio",
        digits=(10, 3),
        help="Used to compute the CO2 debt relatively to the product unit",
    )

    _sql_constraints = [
        ('not_negative_ons_carbon_ratio', 'CHECK(ons_carbon_ratio >= 0)', 'CO2 ratio can not be negative !')
    ]
