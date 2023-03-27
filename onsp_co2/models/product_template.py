from odoo import api, models



class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "carbon.mixin"]

    """
    Add fallback values if product value missing with the following priority order:
        - Product category
    """
    def _get_carbon_value_fallback_records(self):
        res = super(ProductTemplate, self)._get_carbon_value_fallback_records()
        return res + [self.categ_id]

    def _get_carbon_sale_value_fallback_records(self):
        res = super(ProductTemplate, self)._get_carbon_sale_value_fallback_records()
        return res + [self.categ_id]

    @api.depends(
        'categ_id.carbon_value',
        'categ_id.carbon_compute_method',
        'categ_id.carbon_uom_id',
        'categ_id.carbon_monetary_currency_id',
    )
    def _compute_carbon_mode(self):
        super(ProductTemplate, self)._compute_carbon_mode()

    @api.depends(
        'categ_id.carbon_sale_value',
        'categ_id.carbon_sale_compute_method',
        'categ_id.carbon_sale_uom_id',
        'categ_id.carbon_sale_monetary_currency_id',
    )
    def _compute_carbon_sale_mode(self):
        super(ProductTemplate, self)._compute_carbon_sale_mode()
