# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from . import models
from . import report


def _pre_init_carbon(env):
    """Allow installing Sustainability in large databases (>1M records)"""
    CARBON_IN_OUT_MODE = {
        "carbon_in_mode": ("boolean", False),
        "carbon_out_mode": ("boolean", False),
    }

    MODELS_TO_FIELDS_MAPPING = {
        "res.company": {**CARBON_IN_OUT_MODE},
        "res.partner": {**CARBON_IN_OUT_MODE},
        "account.account": {**CARBON_IN_OUT_MODE},
        "product.category": {**CARBON_IN_OUT_MODE},
        "product.product": {**CARBON_IN_OUT_MODE},
        "product.template": {**CARBON_IN_OUT_MODE},
        "product.supplierinfo": {**CARBON_IN_OUT_MODE},
        "res.country": {**CARBON_IN_OUT_MODE},
        "account.move": {
            "carbon_balance": ("float", 0.0),
            "carbon_uncertainty_value": ("float", 0.0),
        },
        "account.move.line": {
            "carbon_origin_json": ("char", "{}"),
            "carbon_debt": ("float", 0.0),
            "carbon_uncertainty_value": ("float", 0.0),
            "carbon_balance": ("float", 0.0),
            "carbon_debit": ("float", 0.0),
            "carbon_credit": ("float", 0.0),
            "carbon_is_date_locked": ("boolean", False),
        },
    }

    fields_spec = []
    for model, fields_mapping in MODELS_TO_FIELDS_MAPPING.items():
        for field_name, (field_type, default_value) in fields_mapping.items():
            fields_spec.append(
                [
                    field_name,  # Field name (ex: carbon_in_mode)
                    model,  # Odoo model name (ex: res.partner)
                    model.replace(".", "_"),  # SQL table name (ex: res_partner)
                    field_type,  # Field type (ex: boolean)
                    False,  # SQL type (ex: boolean) (if nothing, it will be auto-detected)
                    "sustainability",  # Module name (ex: sustainability)
                    default_value,  # Default value (ex: False)
                ]
            )

    openupgrade.add_fields(env, fields_spec)
