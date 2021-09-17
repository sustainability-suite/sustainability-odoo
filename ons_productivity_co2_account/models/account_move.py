# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)
class AccountMove(models.Model):
    _inherit = 'account.move'

    ons_co2_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref("ons_productivity_co2_account.KG_CO2", None),
    )

    ons_carbon_debt = fields.Monetary(
        string="CO2 Debt (Kg)",
        compute="_compute_ons_carbon_debt",
        store=True,
        currency_field='ons_co2_currency_id',
    )

    @api.depends("invoice_line_ids", "invoice_line_ids.ons_carbon_debt")
    def _compute_ons_carbon_debt(self):
        for move in self:
            move.ons_carbon_debt = sum(move.invoice_line_ids.mapped("ons_carbon_balance"))
