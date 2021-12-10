# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License OPL-1 or later (https://www.odoo.com/documentation/14.0/legal/licenses.html#odoo-apps).


from odoo import models, fields

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    ons_co2_currency_id = fields.Many2one(
        'res.currency',
        related="bom_id.ons_co2_currency_id"
    )

    ons_carbon_total = fields.Monetary(
        string="CO2 Total",
        currency_field='ons_co2_currency_id',
        compute="_compute_co2_total",
        store=True,
        help="CO2 Total",
    )

    def _compute_co2_total(self, bom_todo=[]):
        self.ensure_one()
        if self._skip_bom_line(self):
            return 0
        if self.child_bom_id:
            if self.child_bom_id in bom_todo:
                self.child_bom_id._compute_co2_total()
            return self.child_bom_id.ons_carbon_total
        else:
            return self.product_id.ons_get_carbon_credit(self.product_qty)