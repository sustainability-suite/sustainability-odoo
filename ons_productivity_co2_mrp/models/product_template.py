# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License OPL-1 or later (https://www.odoo.com/documentation/14.0/legal/licenses.html#odoo-apps).


from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)



class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    def action_bom_cost(self):
        templates = self.filtered(lambda t: t.product_variant_count == 1 and t.bom_count > 0)
        if templates:
            return templates.mapped('product_variant_id').action_bom_cost()

    def ons_button_bom_cost(self):
        templates = self.filtered(lambda t: t.product_variant_count == 1 and t.bom_count > 0)
        product_ids = templates.mapped('product_variant_id')
        res = product_ids.ons_button_bom_cost()
        for tmpl in templates:
            tmpl.ons_carbon_sale_ratio = tmpl.product_variant_id.ons_carbon_sale_ratio
        return res
