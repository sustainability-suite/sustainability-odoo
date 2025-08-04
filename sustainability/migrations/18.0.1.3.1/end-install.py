import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = util.env(cr)

    compute_method_field_mapping = {
        "physical": "carbon_uom_id",
        "monetary": "carbon_monetary_currency_id",
    }

    for compute_method, field_name in compute_method_field_mapping.items():
        carbon_factors = env["carbon.factor"].search(
            [("carbon_compute_method", "=", compute_method)]
        )
        for carbon_factor in carbon_factors:
            carbon_factor[field_name] = carbon_factor.recent_value_id[field_name]
        _logger.info("Updated %s carbon factors", len(carbon_factors))
