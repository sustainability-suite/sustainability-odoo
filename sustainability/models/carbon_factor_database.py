from odoo import fields, models


class CarbonFactorDatabase(models.Model):
    _name = "carbon.factor.database"
    _description = "Carbon Factor Database"
    _inherit = ["mail.thread", "mail.activity.mixin", "carbon.copy.mixin"]

    name = fields.Char(required=True)
    url = fields.Char()
