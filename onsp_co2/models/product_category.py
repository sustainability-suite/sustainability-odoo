from odoo import api, models

class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "carbon.mixin"]

    def _get_carbon_value_fallback_records(self) -> list:
        res = super(ProductCategory, self)._get_carbon_value_fallback_records()
        return res + [self.parent_id]

    def _get_carbon_sale_value_fallback_records(self) -> list:
        res = super(ProductCategory, self)._get_carbon_sale_value_fallback_records()
        return res + [self.parent_id]

    @api.depends('parent_id.carbon_value')
    def _compute_carbon_value(self):
        super()._compute_carbon_value()

    @api.depends('parent_id.carbon_sale_value')
    def _compute_carbon_sale_value(self):
        super()._compute_carbon_sale_value()
