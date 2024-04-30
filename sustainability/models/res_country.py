from odoo import models


class ResCountry(models.Model):
    _name = "res.country"
    _inherit = ["res.country", "carbon.mixin"]

    # Todo: check if we keep this here (if useful for accounting) or if we move it to a submodule
