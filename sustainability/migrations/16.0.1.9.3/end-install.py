import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    carbon_line_origins = env["carbon.line.origin"].search([])
    for carbon_line_origin in carbon_line_origins:
        carbon_line_origin._compute_quantity()

    _logger.info("Updated %s carbon line origins", len(carbon_line_origins))
