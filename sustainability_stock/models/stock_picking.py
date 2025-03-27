import logging
from datetime import datetime

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

    def _carbon_display_notification(self, message, sticky=False) -> dict:
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

    def _carbon_validate_missing_required_fields(self, company, picking) -> dict | None:
        """
        Validates that all required fields for carbon emissions calculations are present
        in the company configuration and the picking record.
        """
        missing_fields = []
        origin = picking.picking_type_id.warehouse_id.partner_id
        destination = picking.partner_id

        if not company.carbon_freight_climatiq_api_url:
            missing_fields.append(_("Climatiq API URL"))
        if not company.carbon_freight_climatiq_api_key:
            missing_fields.append(_("Climatiq API key"))
        if not company.carbon_freight_transport_mode:
            missing_fields.append(_("Transport mode"))
        if not company.carbon_freight_product_upstream:
            missing_fields.append(_("Product for Upstream Freight"))
        if not company.carbon_freight_product_downstream:
            missing_fields.append(_("Product for Downstream Freight"))
        if not origin:
            missing_fields.append(_("Origin"))
        if not destination:
            missing_fields.append(_("Destination"))

        if missing_fields:
            return self._carbon_display_notification(
                _(
                    f"The following required values are missing or invalid: {', '.join(missing_fields)}"
                )
            )
        return None

    def _compute_carbon_line_origin_qty(self):
        for picking in self:
            origins = self.env["carbon.line.origin"].search(
                [
                    ("move_carbon_freight_picking_id", "=", picking.id),
                ],
            )
            picking.carbon_line_origin_qty = len(origins)

    def _get_address_inline(self, address):
        splitted_address = address.split("\n")
        return ", ".join([a for a in splitted_address if a.strip()])

    def _get_carbon_emissions(self, company, picking) -> tuple:
        """
        Retrieves the carbon emissions from external API based on stock picking details.
        Returns a tuple with the emissions value and a notification in case of error.
        """
        if not picking.shipping_weight:
            return 0, None

        units = ("kg", "lb")
        unit_select_id = int(
            self.env["ir.config_parameter"].sudo().get_param("product.weight_in_lbs")
        )
        weight_unit = units[unit_select_id]

        origin = self._get_address_inline(
            picking.picking_type_id.warehouse_id.partner_id._display_address(
                without_company=True
            )
        )
        destination = self._get_address_inline(
            picking.partner_id._display_address(without_company=True)
        )
        weight = picking.shipping_weight
        transport_mode = (
            picking.partner_id.carbon_freight_transport_mode
            if picking.partner_id.carbon_freight_transport_mode
            else company.carbon_freight_transport_mode
        )
        carbon_freight_tolerance = company.carbon_freight_tolerance

        existing_computation = self.env[
            "sustainability.stock.freight.computation"
        ].search(
            [
                ("origin", "=", origin),
                ("destination", "=", destination),
                ("weight_unit", "=", weight_unit),
                ("transport_mode", "=", transport_mode),
            ],
            limit=1,
        )

        if existing_computation:
            co2 = existing_computation.co2_ratio * weight
            return co2, None

        data = {
            "route": [
                {
                    "location": {"query": origin},
                    "location_options": {"tolerance_km": carbon_freight_tolerance},
                },
                *(
                    [
                        {"transport_mode": "road"},
                        {"transport_mode": company.carbon_freight_transport_mode},
                        {"transport_mode": "road"},
                    ]
                    if company.carbon_freight_transport_mode != "road"
                    else [{"transport_mode": "road"}]
                ),
                {
                    "location": {"query": destination},
                    "location_options": {"tolerance_km": carbon_freight_tolerance},
                },
            ],
            "cargo": {
                "weight": picking.shipping_weight,
                "weight_unit": weight_unit,
            },
        }
        headers = {"Authorization": f"Bearer {company.carbon_freight_climatiq_api_key}"}
        url = company.carbon_freight_climatiq_api_url

        error_message = _(
            "An error occurred while retrieving carbon emissions data. If the issue persists, contact support."
        )

        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            if response.status_code >= 400:
                response_data = response.json()
                logging.error(f"HTTP {response.status_code} {response.text}")
                detailed_error = response_data.get("message", error_message)
                return None, self._carbon_display_notification(
                    detailed_error, sticky=True
                )

            co2 = response.json().get("co2e", 0)
            self.env["sustainability.stock.freight.computation"].create(
                {
                    "origin": origin,
                    "destination": destination,
                    "weight_unit": weight_unit,
                    "transport_mode": transport_mode,
                    "co2_ratio": co2 / weight,
                    "api_response": response.json(),
                }
            )
            return co2, None

        except requests.exceptions.RequestException as err:
            logging.error(f"Request error: {err}")
            return None, self._carbon_display_notification(error_message)

    @api.depends("state")
    def _compute_carbon_debt(self) -> dict | None:
        """
        Computes and sets the carbon debt (CO2 emissions) for stock pickings in 'done' state.
        Creates or updates accounting entries for the carbon emissions.
        """
        company = self.env.company
        carbon_freight_max_delivery_count = company.carbon_freight_max_delivery_count

        if len(self) > carbon_freight_max_delivery_count:
            return self._carbon_display_notification(
                _(
                    f"You cannot process more than {carbon_freight_max_delivery_count} deliveries at once. "
                    "Please edit the setting to increase the limit if needed."
                )
            )

        carbon_freight_product_upstream = company.carbon_freight_product_upstream
        carbon_freight_product_downstream = company.carbon_freight_product_downstream
        carbon_freight_journal_id = company.carbon_freight_journal_id
        carbon_freight_account_id = company.carbon_freight_account_id

        pickings_to_process = self.filtered(lambda p: p.state == "done")

        for picking in pickings_to_process:
            if (
                missing_fields_notification
                := self._carbon_validate_missing_required_fields(company, picking)
            ):
                return missing_fields_notification

            emissions, error = self._get_carbon_emissions(company, picking)
            if error:
                return error

            picking.carbon_debt = emissions

            is_inbound_receipt = picking.picking_type_id.code == "incoming"
            product_id = (
                carbon_freight_product_upstream
                if is_inbound_receipt
                else carbon_freight_product_downstream
            )

            carbon_freight_uncertainty_ratio = (
                company.carbon_freight_uncertainty_percentage / 100
            )

            existing_move = picking.carbon_freight_move_ids[
                :1
            ]  # should be one2one relation
            if existing_move:
                existing_move.button_draft()

                for line in existing_move.line_ids:
                    if line.product_id:
                        line.sudo().write(
                            {
                                "carbon_debt": picking.carbon_debt,
                                "quantity": picking.shipping_weight,
                                "carbon_data_uncertainty_percentage": carbon_freight_uncertainty_ratio,
                                "carbon_uncertainty_value": carbon_freight_uncertainty_ratio
                                * picking.carbon_debt,
                                "carbon_origin_json": {
                                    "mode": "manual",
                                    "details": {
                                        "uid": self.env.uid,
                                        "username": self.env.user.name,
                                    },
                                    "model_name": self._name,
                                },
                            }
                        )
                existing_move.action_post()
            else:
                today = datetime.today().date().strftime("%Y-%m-%d")
                flow = "Upstream" if is_inbound_receipt else "Downstream"
                move = (
                    self.env["account.move"]
                    .sudo()
                    .create(
                        {
                            "ref": f"Freight_Carbon_{flow}_{today}",
                            "journal_id": carbon_freight_journal_id.id,
                            "invoice_date": today,
                            "date": today,
                            "partner_id": picking.partner_id.id,
                            "company_id": company.id,
                            "move_type": "in_invoice",
                            "carbon_freight_picking_id": picking.id,
                            "line_ids": [
                                Command.create(
                                    {
                                        "carbon_debt": picking.carbon_debt,
                                        "carbon_uncertainty_value": carbon_freight_uncertainty_ratio
                                        * picking.carbon_debt,
                                        "carbon_data_uncertainty_percentage": carbon_freight_uncertainty_ratio,
                                        "account_id": carbon_freight_account_id.id,
                                        "product_id": product_id.id,
                                        "debit": 0,
                                        "credit": 0,
                                        "carbon_is_locked": True,
                                        "quantity": picking.shipping_weight,
                                        "carbon_origin_json": {
                                            "mode": "manual",
                                            "details": {
                                                "uid": self.env.uid,
                                                "username": self.env.user.name,
                                            },
                                            "model_name": self._name,
                                        },
                                    },
                                ),
                            ],
                        }
                    )
                )
                move.action_post()

        pickings_not_processed = self - pickings_to_process
        if pickings_not_processed:
            if len(pickings_not_processed) == 1:
                return self._carbon_display_notification(
                    _(
                        "Carbon emission can only be computed for pickings with state 'done'."
                    )
                )
            not_processed_names = ", ".join(str(p.name) for p in pickings_not_processed)
            return self._carbon_display_notification(
                _(
                    f"The following pickings were not processed for carbon computation "
                    f"because they are not in the 'done' state: {not_processed_names}"
                ),
                sticky=True,
            )

        return None

    def action_recompute_carbon(self) -> dict:
        for picking in self:
            picking._compute_carbon_debt()
        return {}

    def action_see_carbon_origins(self) -> dict:
        self.ensure_one()
        return self._generate_action(
            title=_("Carbon Footprint for"),
            model="carbon.line.origin",
            domain=[("move_carbon_freight_picking_id", "=", self.id)],
        )
