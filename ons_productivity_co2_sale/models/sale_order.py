# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

   
    ons_carbon_debt = fields.Float(
        string="CO2 Value",
        compute="_compute_ons_carbon_debt",
        inverse="_inverse_ons_carbon_debt",
        store=True,
        readonly=False,
    )

    @api.depends("order_line", "order_line.ons_carbon_debt")
    def _compute_ons_carbon_debt(self):
        for order in self:
            order.ons_carbon_debt = sum(order.order_line.mapped("ons_carbon_debt"))

    def _inverse_ons_carbon_debt(self):
        for order in self:
            # Handle case where ons_carbon_debt is 0? 
            # How to distribute? All on 1 product? Based on the price?
            ons_carbon_debt = sum(order.order_line.mapped("ons_carbon_debt"))
            debts = {
                line: ons_carbon_debt and line.ons_carbon_debt * order.ons_carbon_debt / ons_carbon_debt
                for line in order.order_line
            }
            for line in order.order_line:
                line.ons_carbon_debt = debts[line]
