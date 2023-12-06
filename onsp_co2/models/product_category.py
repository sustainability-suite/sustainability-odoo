from odoo import api, models
from typing import Any


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "carbon.mixin"]

    def _get_carbon_in_fallback_records(self) -> list[Any]:
        res = super(ProductCategory, self)._get_carbon_in_fallback_records()
        return res + [self.parent_id]

    def _get_carbon_out_fallback_records(self) -> list[Any]:
        res = super(ProductCategory, self)._get_carbon_out_fallback_records()
        return res + [self.parent_id]

    @api.depends('parent_id.carbon_in_factor_id')
    def _compute_carbon_in_mode(self):
        super(ProductCategory, self)._compute_carbon_in_mode()

    @api.depends('parent_id.carbon_out_factor_id')
    def _compute_carbon_out_mode(self):
        super(ProductCategory, self)._compute_carbon_out_mode()
