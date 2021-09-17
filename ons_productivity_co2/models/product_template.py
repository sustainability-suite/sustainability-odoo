# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"


    ons_carbon_ratio = fields.Float(
        string="CO2 Conversion Ratio",
        digits=(10, 3),
        help="Used to compute the CO2 debt relatively to the product unit",
    )

    ons_carbon_sale_ratio = fields.Float(
        string="CO2 Conversion Ratio For Sale",
        digits=(10, 3),
        help="Used to compute the CO2 debt relatively to the product unit",
    )

    ons_carbon_sale_method = fields.Selection(
        [
            ("qty", "Based on Quantity"),
            ("price", "Based on Price"),
        ],
        default="qty",
        required=True,
    )
    
    _sql_constraints = [
        ('not_negative_ons_carbon_ratio', 'CHECK(ons_carbon_ratio >= 0)', 'CO2 ratio can not be negative !')
    ]
