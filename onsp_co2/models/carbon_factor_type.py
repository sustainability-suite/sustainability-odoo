from odoo import fields, models, _

class CarbonFactorType(models.Model):
    _name = "carbon.factor.type"
    _description = "Carbon Factor Type"
    
    code = fields.Char(required=True)
    name = fields.Char('Description', required=True)
