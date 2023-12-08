from odoo import api, models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "carbon.mixin"]

    """
    Add fallback values if product value missing with the following priority order:
        - Product category
    """

    def _get_carbon_in_fallback_records(self):
        res = super()._get_carbon_in_fallback_records()
        return res + [self.categ_id]

    def _get_carbon_out_fallback_records(self):
        res = super()._get_carbon_out_fallback_records()
        return res + [self.categ_id]

    @api.depends("categ_id.carbon_in_factor_id")
    def _compute_carbon_in_mode(self):
        return super()._compute_carbon_in_mode()

    @api.depends("categ_id.carbon_out_factor_id")
    def _compute_carbon_out_mode(self):
        return super()._compute_carbon_out_mode()
