from odoo import fields, models


class CarbonFactorSource(models.Model):
    _name = "carbon.factor.source"
    _description = "Carbon Factor Source"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    
    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    author = fields.Char('Author', required=True)
    url = fields.Char('URL', required=True)
