# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
# from odoo.osv import expression


import logging
_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    _inherit = 'product.category'

    ons_carbon_ratio = fields.Float(
        string="CO2 Conversion Ratio",
        digits=(10, 3),
        help="Used to compute the CO2 debt relatively to a cost",
    )
    ons_carbon_sale_ratio = fields.Float(
        string="CO2 Conversion Ratio For Sale",
        digits=(10, 3),
        help="Used to compute the CO2 debt relatively to the product unit",
    )

    def ons_get_recusive_ratio(self):
        self.ensure_one()
        while self:
            if self.ons_carbon_ratio:
                return self.ons_carbon_ratio
            self = self.parent_id
        return 0

    def ons_get_recusive_sale_ratio(self):
        self.ensure_one()
        while self:
            if self.ons_carbon_sale_ratio:
                return self.ons_carbon_sale_ratio
            self = self.parent_id
        return 0
