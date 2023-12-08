from odoo import fields, models


class CarbonFactorType(models.Model):
    _name = "carbon.factor.type"
    _description = "Carbon Factor Type"
    _inherit = ["carbon.copy.mixin"]

    code = fields.Char(required=True)
    name = fields.Char("Description", required=True)
