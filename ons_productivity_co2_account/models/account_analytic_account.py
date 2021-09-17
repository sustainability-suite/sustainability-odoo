# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    ons_co2_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref("ons_productivity_co2_account.KG_CO2", None),
    )