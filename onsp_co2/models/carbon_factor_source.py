from odoo import fields, models


class CarbonFactorSource(models.Model):
    _name = "carbon.factor.source"
    _description = "Carbon Factor Source"
    _inherit = ["mail.thread", "mail.activity.mixin", "carbon.copy.mixin"]

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    author = fields.Char(required=True)
    url = fields.Char("URL", required=True)
