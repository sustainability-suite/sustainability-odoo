# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ons_carbon_ratio = fields.Float(
        string="CO2 Conversion Ratio",
        digits=(10, 3),
        help="Used to compute the CO2 debt relatively to a cost",
    )

    def ons_get_recusive_ratio(self):
        self.ensure_one()
        while self:
            if self.ons_carbon_ratio:
                return self.ons_carbon_ratio
            self = self.parent_id
        return 0

    _sql_constraints = [
        ('not_negative_ons_carbon_ratio', 'CHECK(ons_carbon_ratio >= 0)', 'CO2 ratio can not be negative !')
    ]
