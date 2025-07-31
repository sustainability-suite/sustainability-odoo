import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = util.env(cr)

    freight_computations = env["sustainability.stock.freight.computation"].search([])
    freight_computations.action_create_carbon_factor()

    _logger.info("Updated %s freight computations", len(freight_computations))
