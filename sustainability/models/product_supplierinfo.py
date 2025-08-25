from odoo import api, models


class ProductSupplierInfo(models.Model):
    _name = "product.supplierinfo"
    _inherit = ["product.supplierinfo", "carbon.mixin"]
    _carbon_types = ["in"]

    def _update_carbon_in_fields(self, vals):
        """
        Helper method to update carbon_in_is_manual and carbon_in_mode based on carbon_in_factor_id.
        """
        if vals.get("carbon_in_factor_id"):
            vals["carbon_in_is_manual"] = True
            vals["carbon_in_mode"] = "manual"
        else:
            vals["carbon_in_is_manual"] = False
            vals["carbon_in_mode"] = "auto"
        return vals

    @api.model
    def create(self, vals):
        vals = self._update_carbon_in_fields(vals)
        return super().create(vals)

    def write(self, vals):
        if "carbon_in_factor_id" in vals:
            vals = self._update_carbon_in_fields(vals)
        return super().write(vals)

    @api.depends("product_uom")
    def _get_allowed_factors_domain(self):
        return (
            super()._get_allowed_factors_domain()
            + self._get_uom_filtered_factors_domain("product_uom")
        )
