# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

# Extract from product on validation and make it readonly then
# Extract on receipt?

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    ons_carbon_debt = fields.Float(
        string="CO2 Debt (Kg)",
    )

    @api.onchange("product_id", "product_qty")
    def _set_ons_carbon_debt(self):
        for line in self.filtered("product_id"):
            debt = self.ons_get_carbon_amount()
            line.ons_carbon_debt = debt

    def ons_get_carbon_amount(self):
        self.ensure_one()
        return self.product_id.ons_get_carbon_debit(
            self.product_qty,
            cost=self.price_subtotal,
            partner_id=self.order_id.partner_id,
            country_id=self.order_id.partner_id.country_id
        )

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        # Handle partially invoiced case
        ratio = self.product_qty and self.qty_to_invoice / self.product_qty
        res["ons_carbon_debt"] = self.ons_carbon_debt * ratio
        return res
    
    def write(self, vals):
        ons_carbon_debt = vals.get("ons_carbon_debt")
        res = super(PurchaseOrderLine, self).write(vals)
        if ons_carbon_debt is not None:
            # Update quantity on invoice_lines
            unitary_carbon = self.product_qty and self.ons_carbon_debt / self.product_qty
            for inv_line_id in self.invoice_lines:
                inv_line_id.ons_carbon_debt = inv_line_id.quantity * unitary_carbon
        return res


    # def unlink(self):
    #     for rec in self:
    #         product_id = rec._get_ons_carbon_product_id()
    #         product_id.ons_carbon_debt += rec.ons_carbon_debt
    #     super(PurchaseOrderLine, self).unlink()
