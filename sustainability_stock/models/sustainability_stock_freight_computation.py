from datetime import datetime
from typing import Any

from odoo import Command, _, api, fields, models
from odoo.tools.safe_eval import safe_eval


class SustainabilityStockFreightComputation(models.Model):
    _name = "sustainability.stock.freight.computation"
    _description = "Freight Computation"

    origin = fields.Char()
    destination = fields.Char()
    co2_ratio = fields.Float()
    weight_unit = fields.Char(string="Unit")
    transport_mode = fields.Char()
    co2_display = fields.Char(
        string="CO2 ratio", compute="_compute_co2_display", store=False
    )
    api_response = fields.Text()
    request_payload = fields.Text()
    error_message = fields.Text()

    @api.depends("co2_ratio", "weight_unit")
    def _compute_co2_display(self):
        for record in self:
            record.co2_display = f"{record.co2_ratio:.6f} kgCO2e/{record.weight_unit}"

    def action_create_carbon_factor(self):
        created_carbon_factors = self.env["carbon.factor"]
        for record in self:
            content = record.api_response
            content = safe_eval(content)
            created_carbon_factors |= created_carbon_factors.sudo().create(
                self._prepare_emission_factor_values(content)
            )

        if not created_carbon_factors:
            return {}
        return {
            "type": "ir.actions.act_window",
            "res_model": "carbon.factor",
            "view_mode": "list,form",
            "target": "current",
            "domain": [("id", "in", created_carbon_factors.ids)],
        }

    @api.model
    def _get_parent_carbon_factor(cls):
        if carbon_factor := cls.env["carbon.factor"].search(
            [("is_climatiq", "=", True), ("parent_id", "=", False)], limit=1
        ):
            return carbon_factor
        return (
            cls.env["carbon.factor"]
            .sudo()
            .create(
                {
                    "name": "Carbon Freight (Climatiq)",
                    "is_climatiq": True,
                }
            )
        )

    @api.model
    def _source_trail_required_fields(cls) -> list[str]:
        return [
            "data_category",
            "name",
            "source",
            "source_dataset",
            "year",
            "region",
            "region_name",
        ]

    @api.model
    def _validate_source_trail(cls, source_trail: dict) -> bool:
        REQUIRED_FIELDS = cls._source_trail_required_fields()
        if not source_trail:
            return False

        if not isinstance(source_trail, dict):
            return False

        if not all(source_trail.get(field) for field in REQUIRED_FIELDS):
            return False

        return True

    @api.model
    def _prepare_emission_factor_values(
        cls, payload: dict[str, Any] | list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        source_trail_list = []
        if isinstance(payload, dict):
            for route in payload.get("route", []):
                possible_source_trail = route.get("source_trail", [])
                for source_trail in possible_source_trail:
                    if cls._validate_source_trail(source_trail):
                        source_trail_list.append(source_trail)
        elif isinstance(payload, list):
            for item in payload:
                if cls._validate_source_trail(item):
                    source_trail_list.append(item)

        carbon_factors_values = []
        already_existing_factors = cls.env["carbon.factor"].search(
            [("is_climatiq", "=", True)]
        )
        for source_trail in source_trail_list:
            if already_existing_factors.filtered(
                lambda f: f.name == source_trail.get("name")  # noqa: B023
            ):
                continue
            carbon_factors_values.append(
                {
                    "carbon_compute_method": "physical",
                    "is_climatiq": True,
                    "parent_id": cls._get_parent_carbon_factor().id,
                    "name": source_trail.get("name"),
                    "value_ids": [
                        Command.create(
                            {
                                "carbon_value": 0.0,
                                "date": datetime.strptime(
                                    source_trail.get("year"), "%Y"
                                ).replace(month=1, day=1),
                                "carbon_uom_id": cls.env.ref("uom.product_uom_km").id,
                            }
                        )
                    ],
                    "comment": _("Generated from Climatiq API"),
                }
            )

        return carbon_factors_values
