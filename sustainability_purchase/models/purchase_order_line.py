from typing import Any

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ["purchase.order.line", "carbon.line.mixin"]

    carbon_supplier_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Supplier Info",
        compute="_compute_carbon_supplier_id",
    )

    def _compute_carbon_supplier_id(self):
        """
        Compute the carbon_supplier_id field.
        Note that since the same seller can be added multiple times to the same product,
        we need to filter the sellers by the partner_id of the order.
        If there are multiple matches,
        we'll take the most recent one.
        """

        for line in self:
            seller = line.product_id.seller_ids.filtered(
                lambda s: s.partner_id.id == line.order_id.partner_id.id  # noqa: B023
            )
            line.carbon_supplier_id = seller[-1] if len(seller) > 1 else seller

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        if self.carbon_is_locked:
            res.update(
                {
                    "carbon_debt": self.carbon_debt,
                    "carbon_uncertainty_value": self.carbon_uncertainty_value,
                    "carbon_data_uncertainty_percentage": self.carbon_data_uncertainty_percentage,
                    "carbon_is_locked": True,
                    "carbon_origin_json": {
                        "mode": "manual",
                        "details": {
                            "uid": self.env.uid,
                            "username": self.env.user.name,
                        },
                    },
                }
            )
        return res

    # --------------------------------------------
    #                  MIXIN
    # --------------------------------------------

    @api.depends(
        # Seller
        "product_id.seller_ids",
        "product_id.seller_ids.carbon_in_factor_id",
        "order_id.partner_id",
        "partner_id",
        # Product
        "product_id.carbon_in_factor_id",
        "product_qty",
        "product_uom",
        "price_subtotal",
        "order_id.date_approve",
        "order_id.currency_id",
    )
    def _compute_carbon_debt(self, force_compute: bool | str | list[str] = None):
        return super()._compute_carbon_debt(force_compute)

    # --- Methods to override ---

    @api.model
    def _get_states_to_auto_recompute(self) -> list[str]:
        return ["draft", "sent"]

    @api.model
    def _get_state_field_name(self) -> str:
        return "state"

    @api.model
    def _get_carbon_compute_possible_fields(self) -> list[str]:
        return ["carbon_supplier_id", "product_id"]

    def _get_lines_to_compute_domain(self, force_compute: list[str]):
        domain = super()._get_lines_to_compute_domain(force_compute)
        domain.append(("display_type", "not in", ["line_section", "line_note"]))
        return domain

    def _get_carbon_compute_kwargs(self) -> dict:
        res = super()._get_carbon_compute_kwargs()
        res.update(
            {
                "carbon_type": "in",
                "date": self.date_approve or self.date_order,
                "from_currency_id": self.currency_id,
                "reference": self.order_id.mapped("name"),
            }
        )
        return res

    def _get_line_amount(self) -> float:
        return self.price_subtotal

    def _get_carbon_compute_default_record(self) -> Any:
        self.ensure_one()
        return self.company_id

    # --- Modular methods ---
    # --- PRODUCT ---

    def can_use_product_id_carbon_value(self) -> bool:
        self.ensure_one()
        return bool(self.product_id) and self.product_id.can_compute_carbon_value("in")

    def get_product_id_carbon_compute_values(self) -> dict:
        self.ensure_one()
        return {
            "quantity": self.product_qty,
            "from_uom_id": self.product_uom,
            "product_id": self.product_id,
        }

    def can_use_carbon_supplier_id_carbon_value(self) -> bool:
        self.ensure_one()
        return bool(
            self.carbon_supplier_id
        ) and self.carbon_supplier_id.can_compute_carbon_value("in")

    def get_carbon_supplier_id_carbon_compute_values(self) -> dict:
        self.ensure_one()
        return self.get_product_id_carbon_compute_values()

    @api.model
    def create(self, vals):
        lines = super().create(vals)
        lines.action_recompute_carbon()
        return lines
