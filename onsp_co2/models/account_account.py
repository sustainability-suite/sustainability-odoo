from odoo import fields, models

class AccountAccount(models.Model):
    _name = "account.account"
    _inherit = ["account.account", "carbon.mixin"]

    use_carbon_value = fields.Boolean(string="Use CO2e value")
