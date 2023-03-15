from odoo import fields, models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "carbon.mixin"]

    carbon_compute_method = fields.Selection(
        [
            ("qty", "Based on Quantity"),
            ("price", "Based on Price"),
        ],
        default="qty",
        string="Compute method",
        required=True,
    )


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


