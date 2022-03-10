# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models, fields, api

class MrpBom(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'

    ons_co2_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref("ons_productivity_co2_account.KG_CO2", None),
    )
    
    ons_carbon_offset = fields.Monetary(
        string="CO2 Offset",
        currency_field='ons_co2_currency_id',
        help="CO2 produced during the processes",
    )    

    ons_carbon_total = fields.Monetary(
        string="CO2 Total",
        currency_field='ons_co2_currency_id',
        compute="_compute_co2_total",
        store=True,
        help="CO2 Total",
    )

    @api.depends(
        "bom_line_ids",
        "bom_line_ids.product_qty"
    )
    def _compute_co2_total(self):
        # output: done == self and todo empty
        self._compute_co2_total_lazy(self)  # self == todo on first level only

    def _compute_co2_total_lazy(self, todo):
        """
            self: bom to computes
            todo: bom that may be computed now if need for bom in self
            The goal of "todo" is to avoid digging deep in recursion

            Nb: Odoo does not allow cyclic dependences (A -> B -> A)
            Otherwise this method wouldn't work

            It uses the ons_carbon_ratio from sub-boms to fill ons_carbon_ratio_sale!
        """
        done = self
        while self:
            bom, self = self[0], self[1:]
            total = self.ons_carbon_offset
            for line in bom.bom_line_ids:
                # if line._skip_bom_line(bom.product_id):
                #     continue

                if line.child_bom_id:
                    if line.child_bom_id in todo:
                        sub_done, todo = line.child_bom_id._compute_co2_total_lazy(todo)
                        done |= sub_done
                        self -= sub_done
                    total += line.child_bom_id.ons_carbon_total
                else:
                    total += line.product_id.ons_get_carbon_credit(line.product_qty)
            bom.ons_carbon_total = total
        return done, todo
