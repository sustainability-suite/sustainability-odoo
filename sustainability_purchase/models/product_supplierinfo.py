from odoo import api, models


class ProductSupplierInfo(models.Model):
    _name = "product.supplierinfo"
    _inherit = ["product.supplierinfo", "carbon.mixin"]

    def _get_carbon_in_fallback_records(self) -> list:
        self.ensure_one()
        res = super()._get_carbon_in_fallback_records()
        return res + [self.partner_id]

    def _get_carbon_out_fallback_records(self) -> list:
        self.ensure_one()
        res = super()._get_carbon_out_fallback_records()
        return res + [self.partner_id]

    @api.model
    def _get_carbon_fields_custom_group(self):
        return (
            "sales_team.group_sale_manager"
        )  # TODO: Change this when the OR is available
