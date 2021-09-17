# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools.float_utils import float_compare
# from odoo.osv import expression


import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    ons_carbon_debt = fields.Float(
        string="CO2 Debt (Kg)",
        readonly=True,  # May change for groups
    )

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

    def ons_get_carbon_debit(self, qty, cost=None, partner_id=None, country_id=None):
        if not self:
            return cost * self.env.user.company_id.ons_carbon_ratio

        self.ensure_one()
        value = qty if self.product_tmpl_id.ons_carbon_sale_method == "qty" else cost
        if self.ons_carbon_sale_ratio > 0:
            return value * self.ons_carbon_sale_ratio
        tmpl_ratio = self.product_tmpl_id.ons_carbon_sale_ratio
        if tmpl_ratio > 0:
            return value * tmpl_ratio
        categ_ratio = self.categ_id.ons_get_recusive_sale_ratio()
        if categ_ratio > 0:
            return value * categ_ratio
        return 0


    def ons_get_carbon_credit(self, qty, cost=None, partner_id=None, country_id=None):
        """
            For consistency, the cost passed must always be in the same currency (normally, the company currency).
            No conversion will be done in this function.
        """
        if not self:
            return cost * self.env.user.company_id.ons_carbon_ratio

        if len(self) > 1:
            return 0
            
        # Take partner from context if None?
        debt = self._ons_get_carbon_credit_by_qty(qty, partner_id)
        if debt:
            return debt
        if not cost:
            return 0
        # Take country_id from partner_id if None?
        return self._ons_get_carbon_credit_by_cost(cost, partner_id, country_id)

    def _ons_get_carbon_credit_by_qty(self, qty, partner_id=None):
        self.ensure_one()
        if qty <= 0:
            return 0
        if partner_id:
            supplier_env = self.env['product.supplierinfo'].sudo()
            supplier_info = supplier_env.search([
                ('ons_carbon_ratio', '>', 0),
                ('product_id', '=', self.id),
                ('name', '=', int(partner_id)),
            ])
            if not supplier_info:
                supplier_info = supplier_env.search([
                    ('ons_carbon_ratio', '>', 0),
                    ('product_tmpl_id', '=', self.product_tmpl_id.id),
                    ('name', '=', int(partner_id)),
                ])
            if supplier_info:
                ratio = supplier_info[0].ons_carbon_ratio
                if ratio:
                    return qty * ratio
        if self.ons_carbon_ratio > 0:
            return qty * self.ons_carbon_ratio
        if self.product_tmpl_id.ons_carbon_ratio > 0:
            return qty * self.product_tmpl_id.ons_carbon_ratio
        # Check from product.category?
        return 0
            
    def _ons_get_carbon_credit_by_cost(self, cost, partner_id=None, country_id=None):
        # Nb: Needs the undiscounted cost
        self.ensure_one()
        if cost <= 0:
            return 0
        categ_ratio = self.categ_id.ons_get_recusive_ratio()
        if categ_ratio:
            return cost * categ_ratio
        if partner_id:
            if isinstance(country_id, int):
                partner_id = self.env["res.partner"].sudo().browse(partner_id)
            ratio = partner_id.ons_get_recusive_ratio()
            if ratio > 0:
                return cost * ratio
        if country_id:
            if isinstance(country_id, int):
                country_id = self.env["res.country"].sudo().browse(country_id)
            if country_id.ons_carbon_ratio > 0:
                return cost * country_id.ons_carbon_ratio
        return cost * self.env.company.ons_carbon_ratio
            

    _sql_constraints = [
        ('not_negative_ons_carbon_ratio', 'CHECK(ons_carbon_ratio >= 0)', 'CO2 ratio can not be negative !'),
        ('not_negative_ons_carbon_sale_ratio', 'CHECK(ons_carbon_sale_ratio >= 0)', 'CO2 ratio (for sale) can not be negative !'),
    ]


