# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'
        
    def ons_get_co2_account_account(self):
        return self.env.company.ons_default_co2_account

    def _compute_ons_carbon_debt(self):
        if not self:
            return
        res = self.env["account.move.line"].read_group(
            [("product_id", "in", self.ids)],
            ["ons_carbon_balance:sum", "ons_carbon_debit:sum"],
            ["product_id"]
        )
        groups = {
            r.get("product_id", (None, None))[0]: r
            for r in res
        }
        for product in self:
            data = groups.get(product.id, {})
            product.ons_carbon_debt = data.get("ons_carbon_balance", 0)

    def _ons_prepare_co2_account_move_line(self, qty, vals=None, is_debit=True, **kw):
        """ Based on sale.order.line _prepare_invoice_line and purchase.order.line _prepare_account_move_line """
        self.ensure_one()
        if vals is None:
            vals = {}
        account = self.ons_get_co2_account_account()
        vals.update({
            'display_type': False,
            'name': self.name,
            'product_id': self.id,
            'product_uom_id': self.uom_id.id,
            'quantity': qty,
            'price_unit': 0,
            'account_id': account.id,
        })

        if is_debit:
            vals.update({
                "ons_carbon_debit": self.ons_get_carbon_debit(qty),
                "ons_carbon_credit": 0,
            })
        else:
            vals.update({
                "ons_carbon_debit": 0,
                "ons_carbon_credit": self.ons_get_carbon_credit(qty),
            })
        return vals
