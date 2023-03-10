from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "carbon.mixin"]

    carbon_compute_method = fields.Selection(
        [
            ("qty", "Based on Quantity"),
            ("price", "Based on Price"),
        ],
        default="qty",
        required=True,
    )

    """
    Add fallback values with the following priority order:
        - Supplier infos + their linked partner (this is a special case where fallback records need to be inserted in the middle of the list)
        - Template
        - Product category
        
    """
    def _get_carbon_value_fallback_records(self) -> list:
        res = super(ProductProduct, self)._get_carbon_value_fallback_records()
        supplierinfo_fallbacks = []
        for seller in self.seller_ids:
            supplierinfo_fallbacks.extend([seller] + seller._get_carbon_value_fallback_records())

        return res + supplierinfo_fallbacks + [self.product_tmpl_id, self.categ_id]

    def _get_carbon_sale_value_fallback_records(self) -> list:
        res = super(ProductProduct, self)._get_carbon_sale_value_fallback_records()
        return res + [self.product_tmpl_id, self.categ_id]


    @api.depends('product_tmpl_id.carbon_value', 'categ_id.carbon_value', 'company_id.carbon_value')
    def _compute_carbon_value(self):
        # Todo: check how often this should be recomputed. Idea: add an `update_mode` field + onchange to make fine grained autocompute
        super()._compute_carbon_value()

    @api.depends('product_tmpl_id.carbon_sale_value', 'categ_id.carbon_sale_value', 'company_id.carbon_sale_value')
    def _compute_carbon_sale_value(self):
        # Todo: check how often this should be recomputed. Idea: add an `update_mode` field + onchange to make fine grained autocompute
        super()._compute_carbon_sale_value()



    def get_carbon_value(self, value_type: str, quantity: float = None, price: float = None) -> float:
        """
        Return a value computed depending on the calculation method of carbon (qty/price) and the type of operation (sale/purchase)
        Used in account.move.line to compute carbon debt if a product is set.
        """
        self.ensure_one()
        if not (quantity or price):
            self.env['res.users'].search([])
            raise UserError(_("You must pass either a quantity or a price to compute carbon cost"))

        value = quantity if self.carbon_compute_method == "qty" else price
        if value is None:
            raise UserError(_("%s carbon value is based on %s but the value was not passed as a parameter", self.display_name, self.carbon_compute_method))

        if value_type == 'debit':
            carbon_value = self.carbon_value
        elif value_type == 'credit':
            carbon_value = self.carbon_sale_value
        else:
            raise UserError(_("value_type parameter must be either `debit` or `credit`"))

        return value * carbon_value




