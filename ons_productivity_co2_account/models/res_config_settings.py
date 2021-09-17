# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ons_default_co2_account = fields.Many2one(
        'account.account',
        string="Default CO2 Account",
        help="",
        related='company_id.ons_default_co2_account',
        readonly=False
    )