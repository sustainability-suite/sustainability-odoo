from odoo import models, fields, api
from typing import Any

class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "carbon.mixin"]

    def _get_carbon_value_fallback_records(self) -> list[Any]:
        res = super(ProductCategory, self)._get_carbon_value_fallback_records()
        return res + [self.parent_id]

    def _get_carbon_sale_value_fallback_records(self) -> list[Any]:
        res = super(ProductCategory, self)._get_carbon_sale_value_fallback_records()
        return res + [self.parent_id]

