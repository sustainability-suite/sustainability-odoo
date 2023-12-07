from odoo import api, models
# from odoo.addons.onsp_co2.models.carbon_mixin import auto_depends


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "carbon.mixin"]
    _fallback_records = ['product_tmpl_id']

    """
    Add fallback values with the following priority order:
        - Supplier infos + their linked partner (this is a special case where fallback records need to be inserted in the middle of the list)
        - Template
        - Product category
        
    """
    def _get_carbon_in_fallback_records(self) -> list:
        res = super(ProductProduct, self)._get_carbon_in_fallback_records()
        return res + [self.product_tmpl_id, self.categ_id]

    def _get_carbon_out_fallback_records(self) -> list:
        res = super(ProductProduct, self)._get_carbon_out_fallback_records()
        return res + [self.product_tmpl_id, self.categ_id]


    @api.depends('product_tmpl_id.carbon_in_factor_id', 'categ_id.carbon_in_factor_id')
    def _compute_carbon_in_mode(self):
        return super(ProductProduct, self)._compute_carbon_in_mode()

    @api.depends('product_tmpl_id.carbon_out_factor_id', 'categ_id.carbon_out_factor_id')
    def _compute_carbon_out_mode(self):
        return super(ProductProduct, self)._compute_carbon_out_mode()



# ProductProduct = auto_depends(ProductProduct)



