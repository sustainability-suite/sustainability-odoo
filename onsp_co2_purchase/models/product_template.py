from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_carbon_in_value_fallback_records(self):
        """
        We add sellers in product.template because does not care about the variant for suppliers anyway...
        If needed, we can split between template and variant (with here seller_ids.filtered(lambda s: not s.product_id))
        """
        res = super(ProductTemplate, self)._get_carbon_in_value_fallback_records()
        supplierinfo_fallbacks = []
        for seller in self.seller_ids:
            supplierinfo_fallbacks.extend([seller] + seller._get_carbon_in_value_fallback_records())
        # Insert suppliers before other values
        return supplierinfo_fallbacks + res

    def _get_carbon_out_value_fallback_records(self):
        res = super(ProductTemplate, self)._get_carbon_out_value_fallback_records()
        return res + [self.categ_id]
