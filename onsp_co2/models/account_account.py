from odoo import fields, models


class AccountAccount(models.Model):
    _name = "account.account"
    _inherit = ["account.account", "carbon.mixin"]

    use_carbon_value = fields.Boolean(string="Use CO2e value", tracking=True)
    carbon_factor_id = fields.Many2one(tracking=True)
    carbon_value = fields.Float(tracking=True)

    # Todo: check if we should always use the same field for all accounts
    # This remark is mainly about company default value, might be nice to get the sale value for income accounts.

