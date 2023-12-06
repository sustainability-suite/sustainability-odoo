from odoo import models


class ProductSupplierInfo(models.Model):
    _name = "product.supplierinfo"
    _inherit = ["product.supplierinfo", "carbon.mixin"]

    def _get_carbon_in_fallback_records(self) -> list:
        self.ensure_one()
        res = super(ProductSupplierInfo, self)._get_carbon_in_fallback_records()
        return res + [self.partner_id]

    def _get_carbon_out_fallback_records(self) -> list:
        self.ensure_one()
        res = super(ProductSupplierInfo, self)._get_carbon_out_fallback_records()
        return res + [self.partner_id]
