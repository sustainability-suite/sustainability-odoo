# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    ons_carbon_debt = fields.Float(
        string="CO2 Debt (Kg)",
    )

    @api.onchange("product_id", "product_uom_qty", "price_subtotal")
    def _set_ons_carbon_debt(self):
        for line in self.filtered("product_id"):
            debt = line.product_id.ons_get_carbon_debit(line.product_uom_qty, cost=line.price_subtotal)
            line.ons_carbon_debt = debt

    
    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        # invoiced_co2 = sum(self.invoice_lines.mapped("ons_carbon_debt"))
        ratio = self.product_uom_qty / res['quantity'] if res['quantity'] else 0
        res["ons_carbon_debt"] = self.ons_carbon_debt * ratio
        return res
