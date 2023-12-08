import logging

from odoo import fields

_logger = logging.getLogger(__name__)


def create_carbon_factor(env, models: list[str] = None):
    for model in models:
        in_records = env[model].search(
            [("carbon_in_is_manual", "=", True), ("carbon_in_factor_id", "=", False)]
        )
        out_records = env[model].search(
            [("carbon_out_is_manual", "=", True), ("carbon_out_factor_id", "=", False)]
        )

        _create_carbon_factor(in_records, "in")
        _create_carbon_factor(out_records, "out")


def _create_carbon_factor(records, carbon_type):
    if not records:
        return
    today = fields.Date.today()
    prefix = f"carbon_{carbon_type}"

    _logger.info(f"--- Creating carbon {carbon_type} factor for {records._name}")

    for rec in records:
        _logger.info(f"New carbon factor for {rec.name}")
        rec.write(
            {
                f"{prefix}_factor_id": rec.env["carbon.factor"]
                .create(
                    {
                        "name": f"[MIG]{rec.name} ({rec._name} - {carbon_type})",
                        "carbon_compute_method": rec[f"{prefix}_compute_method"],
                        "value_ids": [
                            (
                                0,
                                0,
                                {
                                    "date": today,
                                    "carbon_value": rec[f"{prefix}_value"],
                                    "carbon_uom_id": rec[f"{prefix}_uom_id"].id,
                                    "carbon_monetary_currency_id": rec[
                                        f"{prefix}_monetary_currency_id"
                                    ].id,
                                },
                            )
                        ],
                    }
                )
                .id,
            }
        )
