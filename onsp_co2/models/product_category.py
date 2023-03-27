from odoo import api, models
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

    @api.depends(
        'parent_id.carbon_value',
        'parent_id.carbon_compute_method',
        'parent_id.carbon_uom_id',
        'parent_id.carbon_monetary_currency_id',
    )
    def _compute_carbon_mode(self):
        super(ProductCategory, self)._compute_carbon_mode()

    @api.depends(
        'parent_id.carbon_sale_value',
        'parent_id.carbon_sale_compute_method',
        'parent_id.carbon_sale_uom_id',
        'parent_id.carbon_sale_monetary_currency_id',
    )
    def _compute_carbon_sale_mode(self):
        super(ProductCategory, self)._compute_carbon_sale_mode()
