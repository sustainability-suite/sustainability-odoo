from odoo import api, fields, models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "carbon.mixin"]
    _fallback_records = ["categ_id"]

    """
    Add fallback values if product value missing with the following priority order:
        - Product category
    """

    carbon_line_origin_ids = fields.One2many(
        comodel_name="carbon.line.origin",
        inverse_name="move_line_product_tmpl_id",
        string="Origins",
    )

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

    @api.depends("uom_id")
    def _get_allowed_factors_domain(self):
        return (
            super()._get_allowed_factors_domain()
            + self._get_uom_filtered_factors_domain()
        )
