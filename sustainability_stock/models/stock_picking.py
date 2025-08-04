import logging
from datetime import datetime
from typing import Any

import requests

from odoo import Command, _, api, fields, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "carbon.common.mixin"]

    carbon_debt = fields.Monetary(
        string="CO2",
        currency_field="carbon_currency_id",
        compute="_compute_carbon_debt",
        store=True,
    )
    carbon_freight_move_ids = fields.One2many(
        inverse_name="carbon_freight_picking_id", comodel_name="account.move"
    )
    carbon_currency_id = fields.Many2one(
        "res.currency",
        string="Carbon Currency",
        default=lambda self: self.env.ref("sustainability.carbon_kilo").id,
    )
    carbon_line_origin_qty = fields.Integer(compute="_compute_carbon_line_origin_qty")

    def _carbon_display_notification(self, message: str, sticky: bool = False) -> dict:
        """Display a carbon computation error notification."""
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Carbon Computation Error"),
                "message": message,
                "type": "warning",
                "sticky": sticky,
            },
        }

    @api.model
    def _get_required_fields_mapping(self, company) -> dict[Any, str]:
        """Get mapping of required fields to their error messages."""
        origin = self.picking_type_id.warehouse_id.partner_id
        destination = self.partner_id

        return {
            company.carbon_freight_climatiq_api_url: _("Climatiq API URL"),
            company.carbon_freight_climatiq_api_key: _("Climatiq API key"),
            company.carbon_freight_transport_mode: _("Transport mode"),
            company.carbon_freight_product_upstream: _("Product for Upstream Freight"),
            company.carbon_freight_product_downstream: _(
                "Product for Downstream Freight"
            ),
            origin: _("Origin"),
            destination: _("Destination"),
        }

    def _carbon_validate_missing_required_fields(self, company) -> dict | None:
        """
        Validates that all required fields for carbon emissions calculations are present
        in the company configuration and the picking record.
        """
        self.ensure_one()
        fields_mapping = self._get_required_fields_mapping(company)
        missing_fields = [
            error_message
            for field, error_message in fields_mapping.items()
            if not field
        ]

        if missing_fields:
            return self._carbon_display_notification(
                _(
                    f"The following required values are missing or invalid: {', '.join(missing_fields)}"
                )
            )
        return None

    @api.model
    def _get_address_inline(self, address: str) -> str:
        """Convert multi-line address to single line format."""
        if not address:
            return ""
        splitted_address = address.split("\n")
        return ", ".join([a.strip() for a in splitted_address if a.strip()])

    @api.model
    def _get_formatted_address(self, partner) -> str:
        """Get formatted address from partner."""
        if not partner:
            return ""
        address = partner._display_address(without_company=True)
        return self._get_address_inline(address)

    @api.model
    def _get_weight_unit(self) -> str:
        """Get the weight unit based on system configuration."""
        units = ("kg", "lb")
        unit_select_id = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("product.weight_in_lbs", "0")
        )
        return units[unit_select_id]

    @api.model
    def _get_transport_mode(self, company) -> str:
        """Get transport mode from partner or fallback to company default."""
        return (
            self.partner_id.carbon_freight_transport_mode
            or company.carbon_freight_transport_mode
        )

    @api.model
    def _get_cached_computation(
        self, origin: str, destination: str, weight_unit: str, transport_mode: str
    ) -> Any | None:
        """Get cached computation if it exists."""
        return self.env["sustainability.stock.freight.computation"].search(
            [
                ("origin", "=", origin),
                ("destination", "=", destination),
                ("weight_unit", "=", weight_unit),
                ("transport_mode", "=", transport_mode),
            ],
            limit=1,
        )

    @api.model
    def _log_computation(
        self,
        origin: str,
        destination: str,
        weight_unit: str,
        transport_mode: str,
        co2_ratio: float,
        api_response: dict | None,
        payload: str,
        error_message: str,
    ) -> Any:
        """Log computation results for caching and debugging."""
        cache_record = self.env["sustainability.stock.freight.computation"].create(
            {
                "origin": origin,
                "destination": destination,
                "weight_unit": weight_unit,
                "transport_mode": transport_mode,
                "co2_ratio": co2_ratio,
                "api_response": api_response,
                "request_payload": payload,
                "error_message": error_message,
            }
        )
        cache_record.action_create_carbon_factor()

        return cache_record

    @api.model
    def _build_climatiq_route(
        self, origin: str, destination: str, transport_mode: str, tolerance_km: int
    ) -> list:
        """Build the route structure for Climatiq API request."""
        base_route = [
            {
                "location": {"query": origin},
                "location_options": {"tolerance_km": tolerance_km},
            }
        ]

        # Add transport mode segments
        if transport_mode != "road":
            transport_segments = [
                {"transport_mode": "road"},
                {"transport_mode": transport_mode},
                {"transport_mode": "road"},
            ]
        else:
            transport_segments = [{"transport_mode": "road"}]

        base_route.extend(transport_segments)

        base_route.append(
            {
                "location": {"query": destination},
                "location_options": {"tolerance_km": tolerance_km},
            }
        )

        return base_route

    @api.model
    def _build_climatiq_payload(
        self,
        origin: str,
        destination: str,
        weight: float,
        weight_unit: str,
        transport_mode: str,
        tolerance_km: int,
    ) -> dict[str, Any]:
        """Build the complete payload for Climatiq API request."""
        route = self._build_climatiq_route(
            origin, destination, transport_mode, tolerance_km
        )

        return {
            "route": route,
            "cargo": {
                "weight": weight,
                "weight_unit": weight_unit,
            },
        }

    @api.model
    def _make_climatiq_request(
        self, url: str, api_key: str, payload: dict[str, Any], timeout: int = 30
    ) -> tuple[float | None, dict | None, dict | None]:
        """Make HTTP request to Climatiq API and handle response."""
        headers = {"Authorization": f"Bearer {api_key}"}
        error_message = _(
            "An error occurred while retrieving carbon emissions data. If the issue persists, contact support."
        )

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=timeout
            )
            response_data = response.json()

            if response.status_code >= 400:
                logging.error(f"HTTP {response.status_code} {response.text}")
                detailed_error = response_data.get("message", error_message)
                return (
                    None,
                    self._carbon_display_notification(detailed_error, sticky=True),
                    response_data,
                )

            co2 = response_data.get("co2e", 0)
            return co2, None, response_data

        except requests.exceptions.RequestException as err:
            logging.error(f"Request error: {err}")
            return None, self._carbon_display_notification(error_message), None

    def _get_carbon_emissions(self, company) -> tuple[float | None, dict | None]:
        """
        Retrieves the carbon emissions from external API based on stock picking details.
        Returns a tuple with the emissions value and a notification in case of error.
        """
        self.ensure_one()
        if not self.shipping_weight:
            return 0, None

        # Get basic parameters
        weight_unit = self._get_weight_unit()
        origin = self._get_formatted_address(
            self.picking_type_id.warehouse_id.partner_id
        )
        destination = self._get_formatted_address(self.partner_id)
        weight = self.shipping_weight
        transport_mode = self._get_transport_mode(company)
        tolerance_km = company.carbon_freight_tolerance

        # Check cache first
        existing_computation = self._get_cached_computation(
            origin, destination, weight_unit, transport_mode
        )

        if existing_computation:
            co2 = existing_computation.co2_ratio * weight
            return co2, None

        # Build API request
        payload = self._build_climatiq_payload(
            origin, destination, weight, weight_unit, transport_mode, tolerance_km
        )

        # Make API request
        co2, error, response_data = self._make_climatiq_request(
            company.carbon_freight_climatiq_api_url,
            company.carbon_freight_climatiq_api_key,
            payload,
        )

        if error:
            self._log_computation(
                origin=origin,
                destination=destination,
                weight_unit=weight_unit,
                transport_mode=transport_mode,
                co2_ratio=0,
                api_response=response_data,
                payload=str(payload),
                error_message=str(error),
            )
            return None, error

        # Log successful computation
        co2_ratio = co2 / weight if weight > 0 else 0
        self._log_computation(
            origin=origin,
            destination=destination,
            weight_unit=weight_unit,
            transport_mode=transport_mode,
            co2_ratio=co2_ratio,
            api_response=response_data,
            payload=str(payload),
            error_message="",
        )

        return co2, None

    @api.model
    def _get_carbon_product(self, company) -> Any:
        """Get the appropriate carbon product based on picking type."""
        self.ensure_one()
        is_inbound_receipt = self.picking_type_id.code == "incoming"
        return (
            company.carbon_freight_product_upstream
            if is_inbound_receipt
            else company.carbon_freight_product_downstream
        )

    @api.model
    def _get_carbon_origin_json(self, **details) -> dict[str, Any]:
        """Get carbon origin JSON structure."""
        return {
            "mode": "manual",
            "details": {
                "uid": self.env.uid,
                "username": self.env.user.name,
                **details,
            },
            "model_name": self._name,
        }

    def _update_existing_carbon_move(
        self, existing_move, product_id, carbon_freight_uncertainty_ratio: float
    ) -> None:
        """Update existing carbon accounting move."""
        self.ensure_one()
        existing_move.button_draft()

        existing_move.with_context(dynamic_unlink=True).line_ids.unlink()

        existing_move.sudo().write(
            {
                "line_ids": self._get_carbon_move_line_vals(
                    existing_move.company_id,
                    product_id,
                    carbon_freight_uncertainty_ratio,
                )
            }
        )

        existing_move.action_post()

    def _get_carbon_move_line_vals(
        self, company, product_id, carbon_freight_uncertainty_ratio: float
    ) -> list:
        self.ensure_one()

        weight_unit = self._get_weight_unit()
        origin = self._get_formatted_address(
            self.picking_type_id.warehouse_id.partner_id
        )
        destination = self._get_formatted_address(self.partner_id)
        transport_mode = self._get_transport_mode(company)

        existing_computation = self._get_cached_computation(
            origin, destination, weight_unit, transport_mode
        )

        default_vals = {
            "carbon_debt": self.carbon_debt,
            "carbon_uncertainty_value": carbon_freight_uncertainty_ratio
            * self.carbon_debt,
            "carbon_data_uncertainty_percentage": carbon_freight_uncertainty_ratio,
            "account_id": company.carbon_freight_account_id.id,
            "product_id": product_id.id,
            "debit": 0,
            "credit": 0,
            "carbon_is_locked": True,
            "quantity": self.shipping_weight,
            "carbon_origin_json": self._get_carbon_origin_json(),
        }
        if not existing_computation:
            return [Command.create(default_vals)]

        existing_computation._compute_route_ratio()

        return [
            Command.create(
                {
                    **default_vals,
                    # "carbon_factor_id": factor_id,
                    "carbon_is_locked": True,
                    "carbon_debt": self.carbon_debt * factor_ratio,
                    "carbon_origin_json": self._get_carbon_origin_json(
                        factor_id=factor_id
                    ),
                }
            )
            for factor_id, factor_ratio in existing_computation.route_ratio.items()
        ]

    def _create_new_carbon_move(
        self, company, product_id, carbon_freight_uncertainty_ratio: float
    ) -> None:
        """Create new carbon accounting move."""
        self.ensure_one()
        today = datetime.today().date().strftime("%Y-%m-%d")
        is_inbound_receipt = self.picking_type_id.code == "incoming"
        flow = "Upstream" if is_inbound_receipt else "Downstream"

        move = (
            self.env["account.move"]
            .sudo()
            .create(
                {
                    "ref": f"Freight_Carbon_{flow}_{today}",
                    "journal_id": company.carbon_freight_journal_id.id,
                    "invoice_date": today,
                    "date": today,
                    "partner_id": self.partner_id.id,
                    "company_id": company.id,
                    "move_type": "in_invoice",
                    "carbon_freight_picking_id": self.id,
                    "line_ids": self._get_carbon_move_line_vals(
                        company, product_id, carbon_freight_uncertainty_ratio
                    ),
                }
            )
        )
        move.action_post()

    def _handle_carbon_accounting(self, company) -> None:
        """Handle carbon accounting move creation or update."""
        self.ensure_one()
        product_id = self._get_carbon_product(company)
        carbon_freight_uncertainty_ratio = (
            company.carbon_freight_uncertainty_percentage / 100
        )

        existing_move = self.carbon_freight_move_ids[:1]

        if existing_move:
            self._update_existing_carbon_move(
                existing_move, product_id, carbon_freight_uncertainty_ratio
            )
        else:
            self._create_new_carbon_move(
                company, product_id, carbon_freight_uncertainty_ratio
            )

    @api.depends("state")
    def _compute_carbon_debt(self) -> dict | None:
        """
        Computes and sets the carbon debt (CO2 emissions) for stock pickings in 'done' state.
        Creates or updates accounting entries for the carbon emissions.
        """
        pickings_to_process = self.filtered(lambda p: p.state == "done")

        if not pickings_to_process:
            return self._carbon_display_notification(
                _(
                    "Carbon emission can only be computed for pickings with state 'done'."
                )
            )

        for picking in pickings_to_process:
            company = picking.company_id

            # Validate processing limits
            if self._exceeds_delivery_limit(pickings_to_process, company):
                return self._carbon_display_notification(
                    _(
                        f"You cannot process more than {company.carbon_freight_max_delivery_count} deliveries at once. "
                        "Please edit the setting to increase the limit if needed."
                    )
                )

            # Validate required fields
            if (
                missing_fields_notification
                := picking._carbon_validate_missing_required_fields(company)
            ):
                return missing_fields_notification

            # Get carbon emissions
            emissions, error = picking._get_carbon_emissions(company)
            if error:
                return error

            picking.carbon_debt = emissions

            # Handle accounting
            picking._handle_carbon_accounting(company)

        return self._handle_pickings_not_processed(pickings_to_process)

    @api.model
    def _exceeds_delivery_limit(self, pickings_to_process, company) -> bool:
        """Check if processing exceeds the delivery limit."""
        company_pickings = pickings_to_process.filtered(
            lambda p: p.company_id == company
        )
        return len(company_pickings) > (company.carbon_freight_max_delivery_count or 10)

    def _handle_pickings_not_processed(self, pickings_to_process) -> dict | None:
        """Handle pickings that were not processed."""
        pickings_not_processed = self - pickings_to_process
        if not pickings_not_processed:
            return None

        not_processed_names = ", ".join(str(p.name) for p in pickings_not_processed)
        return self._carbon_display_notification(
            _(
                f"The following pickings were not processed for carbon computation "
                f"because they are not in the 'done' state: {not_processed_names}"
            ),
            sticky=True,
        )

    def _compute_carbon_line_origin_qty(self):
        """Compute the quantity of carbon line origins."""
        for picking in self:
            origins = self.env["carbon.line.origin"].search(
                [
                    ("move_carbon_freight_picking_id", "=", picking.id),
                ]
            )
            picking.carbon_line_origin_qty = len(origins)

    def action_recompute_carbon(self) -> dict:
        """Recompute carbon debt for selected pickings."""
        for picking in self:
            picking._compute_carbon_debt()
        return {}

    def action_see_carbon_origins(self) -> dict:
        """Open carbon origins view for the picking."""
        self.ensure_one()
        return self._generate_action(
            model="carbon.line.origin",
            domain=[("move_carbon_freight_picking_id", "=", self.id)],
        )
