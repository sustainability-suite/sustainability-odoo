# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'
    _description = 'Product'

    def ons_button_bom_cost(self):
        self.ons_action_bom_cost()
        for product in self:
            product._ons_set_co2_from_bom()

    def ons_action_bom_cost(self):
        if not self:
            return
        boms_to_recompute = self.env['mrp.bom'].search(
            [
                '|',
                    ('product_id', 'in', self.ids),
                    '&',
                        ('product_id', '=', False),
                        ('product_tmpl_id', 'in', self.mapped('product_tmpl_id').ids),
            ]
        )
        boms_to_recompute._compute_co2_total()
        for product in self:
            product._ons_set_co2_from_bom()

    def _ons_set_co2_from_bom(self):
        self.ensure_one()
        bom = self.env['mrp.bom']._bom_find(products=self).get(self)
        if bom:
            self.ons_carbon_sale_ratio = bom.ons_carbon_total

