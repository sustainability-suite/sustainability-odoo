from typing import Any, Union

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ["purchase.order.line", "carbon.line.mixin"]

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
        "product_id.carbon_in_factor_id",
        "product_qty",
        "product_uom",
        "price_subtotal",
        "order_id.date_approve",
        "order_id.currency_id",
    )
    def _compute_carbon_debt(self, force_compute: Union[bool, str, list[str]] = None):
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
        return ["product_id"]

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
        return {"quantity": self.product_qty, "from_uom_id": self.product_uom}
