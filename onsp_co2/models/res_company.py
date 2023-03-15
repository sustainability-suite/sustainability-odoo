from odoo import fields, models


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "carbon.mixin"]

    # For companies, carbon value is not linked to a factor and must be a plain value
    # -> We negate a lot of computation
    carbon_value = fields.Float(compute=False, store=True, readonly=False, tracking=True)
    carbon_sale_value = fields.Float(compute=False, store=True, readonly=False, tracking=True)

    carbon_value_origin = fields.Char(compute=False, store=True, default="")
    carbon_sale_value_origin = fields.Char(compute=False, store=True, default="")

    invoice_report_footer = fields.Html(translate=True)

