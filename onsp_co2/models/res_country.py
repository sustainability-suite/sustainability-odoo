from odoo import models

class ResCountry(models.Model):
    _name = "res.country"
    _inherit = ["res.country", "carbon.mixin"]

