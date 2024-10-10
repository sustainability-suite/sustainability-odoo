from odoo import fields, models


class CarbonFactorContributor(models.Model):
    _name = "carbon.factor.contributor"
    _description = "Carbon Factor Contributor"
    _inherit = ["mail.thread", "mail.activity.mixin", "carbon.copy.mixin"]

    name = fields.Char(required=True)
