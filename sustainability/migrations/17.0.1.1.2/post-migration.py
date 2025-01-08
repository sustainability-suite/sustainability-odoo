from odoo import SUPERUSER_ID, api

from odoo.addons.sustainability.models.carbon_mixin import CARBON_MODELS


def migrate(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    models = CARBON_MODELS
    models.remove("carbon.factor")
    models.remove("res.partner")

    for model in models:
        if model not in env:
            continue
        for record in env[model].search(
            [
                "|",
                "|",
                ("carbon_in_is_manual", "!=", False),
                ("carbon_in_factor_id", "=", False),
                "|",
                ("carbon_out_is_manual", "!=", False),
                ("carbon_out_factor_id", "=", False),
            ]
        ):
            if record.carbon_in_is_manual and not record.carbon_in_factor_id:
                record.carbon_in_is_manual = False

            if record.carbon_out_is_manual and not record.carbon_out_factor_id:
                record.carbon_out_is_manual = False
