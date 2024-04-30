from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_carbon_in_fallback_records(self):
        """
        We add sellers in product.template because does not care about the variant for suppliers anyway...
        If needed, we can split between template and variant (with here seller_ids.filtered(lambda s: not s.product_id))
        """
        res = super()._get_carbon_in_fallback_records()
        supplierinfo_partners = [s.partner_id for s in self.seller_ids]
        return supplierinfo_partners + res

    @api.depends("seller_ids.partner_id.carbon_in_factor_id")
    def _compute_carbon_in_mode(self):
        super()._compute_carbon_in_mode()
