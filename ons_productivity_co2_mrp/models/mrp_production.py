# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    ons_co2_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref("ons_productivity_co2_account.KG_CO2", None),
    )

    ons_carbon_offset = fields.Monetary(
        string="CO2 Offset",
        currency_field='ons_co2_currency_id',
        help="CO2 produced during the processes"
    )

    ons_carbon_account_move = fields.Many2one(
        'account.move',
        string="CO2 Account Move",
        readonly=True,
    )

    @api.onchange("bom_id", "product_qty")
    def _set_co2_offset(self):
        for prod in self:
            prod.ons_carbon_offset = (
                prod.bom_id.ons_carbon_offset * prod.product_qty
            )

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        # self.ons_generate_co2_account_move()
        return res

    def ons_get_co2_account_account(self):
        return self.env.company.ons_default_co2_account

    def ons_generate_co2_account_move(self):
        res = self.env["account.move"].browse()
        for mrp in self:
            move = mrp._ons_generate_co2_account_move()
            res |= move
        return res

    def _ons_generate_co2_account_move(self):
        self.ensure_one()
        if not self.ons_carbon_account_move:
            data = self._ons_prepare_co2_account_move()
            move = self.env["account.move"].create(data)
            self.ons_carbon_account_move = move
        return self.ons_carbon_account_move

    def _ons_prepare_co2_account_move(self):
        self.ensure_one()
        line_ids = self._ons_prepare_co2_account_move_lines()
        res = {
            "name": "CO2 " + self.name,
            "move_type": "entry",
            "line_ids": [
                (0, 0, line)
                for line in line_ids
            ],
        }
        return res

    def _ons_prepare_co2_account_move_lines(self):
        self.ensure_one()

        lines = [
            move._ons_prepare_co2_account_move_line(is_debit=False)
            for move in self.move_raw_ids
        ]

        consummed = sum(l.get("ons_carbon_debit", 0) for l in lines)
        finished_move = self.product_id._ons_prepare_co2_account_move_line(
            self.product_qty,
            is_debit=True,
        )
        finished_move["ons_carbon_credit"] = consummed + self.ons_carbon_offset
        
        return [finished_move] + lines