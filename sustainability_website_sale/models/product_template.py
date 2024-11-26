from odoo import fields, models

# from odoo.addons.sustainability.models.carbon_mixin import auto_depends


class ProductTemplate(models.Model):
    _inherit = "product.template"

    carbon_out_factor_value = fields.Float(related="carbon_out_factor_id.carbon_value")
