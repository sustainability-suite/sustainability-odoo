# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'


    ons_co2_currency_id = fields.Many2one(
        'res.currency',
        related='move_id.ons_co2_currency_id',
        readonly=True,
    )

    ons_carbon_debt = fields.Monetary(
        string="CO2 Debt (Kg)",
        currency_field='ons_co2_currency_id',
    )