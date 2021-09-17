# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

        
    def _ons_prepare_co2_account_move_line(self, vals=None, is_debit=True, **kw):
        """ Based on sale.order.line _prepare_invoice_line and purchase.order.line _prepare_account_move_line """
        self.ensure_one()
        return self.product_id._ons_prepare_co2_account_move_line(
            self.product_qty,
            vals=vals,
            is_debit=is_debit,
            **kw,
        )
