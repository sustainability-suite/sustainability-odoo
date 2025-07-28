import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = util.env(cr)

    carbon_line_origins = env["carbon.line.origin"].search([])
    for carbon_line_origin in carbon_line_origins:
        carbon_line_origin._compute_quantity()

    _logger.info("Updated %s carbon line origins", len(carbon_line_origins))
