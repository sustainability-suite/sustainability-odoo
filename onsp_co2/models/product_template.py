from odoo import api, models



class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "carbon.mixin"]

    """
    Add fallback values if product value missing with the following priority order:
        - Product category
    """
    def _get_carbon_in_value_fallback_records(self):
        res = super(ProductTemplate, self)._get_carbon_in_value_fallback_records()
        return res + [self.categ_id]

    def _get_carbon_out_value_fallback_records(self):
        res = super(ProductTemplate, self)._get_carbon_out_value_fallback_records()
        return res + [self.categ_id]

    @api.depends(
        'categ_id.carbon_in_value',
        'categ_id.carbon_in_compute_method',
        'categ_id.carbon_in_uom_id',
        'categ_id.carbon_in_monetary_currency_id',
    )
    def _compute_carbon_in_mode(self):
        super(ProductTemplate, self)._compute_carbon_in_mode()

    @api.depends(
        'categ_id.carbon_out_value',
        'categ_id.carbon_out_compute_method',
        'categ_id.carbon_out_uom_id',
        'categ_id.carbon_out_monetary_currency_id',
    )
    def _compute_carbon_out_mode(self):
        super(ProductTemplate, self)._compute_carbon_out_mode()
