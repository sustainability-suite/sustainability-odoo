from odoo import api, models, _
from odoo.exceptions import UserError
# from odoo.addons.onsp_co2.models.carbon_mixin import auto_depends


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "carbon.mixin"]
    _fallback_records = ['product_tmpl_id']

    """
    Add fallback values with the following priority order:
        - Supplier infos + their linked partner (this is a special case where fallback records need to be inserted in the middle of the list)
        - Template
        - Product category
        
    """
    def _get_carbon_value_fallback_records(self) -> list:
        res = super(ProductProduct, self)._get_carbon_value_fallback_records()
        return res + [self.product_tmpl_id, self.categ_id]

    def _get_carbon_sale_value_fallback_records(self) -> list:
        res = super(ProductProduct, self)._get_carbon_sale_value_fallback_records()
        return res + [self.product_tmpl_id, self.categ_id]


    @api.depends(
        'product_tmpl_id.carbon_value',
        'product_tmpl_id.carbon_compute_method',
        'product_tmpl_id.carbon_uom_id',
        'product_tmpl_id.carbon_monetary_currency_id',
        'categ_id.carbon_value',
        'categ_id.carbon_compute_method',
        'categ_id.carbon_uom_id',
        'categ_id.carbon_monetary_currency_id',
    )
    def _compute_carbon_mode(self):
        super(ProductProduct, self)._compute_carbon_mode()

    @api.depends(
        'product_tmpl_id.carbon_sale_value',
        'product_tmpl_id.carbon_sale_compute_method',
        'product_tmpl_id.carbon_sale_uom_id',
        'product_tmpl_id.carbon_sale_monetary_currency_id',
        'categ_id.carbon_sale_value',
        'categ_id.carbon_sale_compute_method',
        'categ_id.carbon_sale_uom_id',
        'categ_id.carbon_sale_monetary_currency_id',
    )
    def _compute_carbon_sale_mode(self):
        super(ProductProduct, self)._compute_carbon_sale_mode()


    def get_carbon_value(self, value_type: str, quantity: float = None, price: float = None) -> tuple[float, tuple]:
        """
        Return a value computed depending on the calculation method of carbon (qty/price) and the type of operation (credit/debit)
        Used in account.move.line to compute carbon debt if a product is set.
        """
        self.ensure_one()
        if quantity is None and price is None:
            raise UserError(_("You must pass either a quantity or a price to compute carbon cost (product: %s, quantity: %s, price: %s)", self.display_name, quantity, price))

        if value_type == 'debit':
            carbon_value = self.carbon_value
            compute_method = self.carbon_compute_method
        elif value_type == 'credit':
            carbon_value = self.carbon_sale_value
            compute_method = self.carbon_sale_compute_method
        else:
            raise UserError(_("value_type parameter must be either `debit` or `credit`"))

        value = quantity if compute_method == "physical" else price
        if value is None:
            raise UserError(_("%s carbon value is computed with a %s value but this latter was not passed as a parameter", self.display_name, compute_method))

        return value * carbon_value, (carbon_value, compute_method)



# ProductProduct = auto_depends(ProductProduct)



