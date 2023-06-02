from odoo import api, fields, models


class AccountAccount(models.Model):
    _name = "account.account"
    _inherit = ["account.account", "carbon.mixin"]

    @api.model
    def _get_available_carbon_compute_methods(self):
        return [
            ('monetary', 'Monetary'),
        ]

    use_carbon_value = fields.Boolean(string="Use CO2e values", tracking=True)
    carbon_in_factor_id = fields.Many2one(tracking=True, domain="[('carbon_compute_method', '=', 'monetary')]")
    carbon_in_value = fields.Float(tracking=True)

    carbon_in_compute_method = fields.Selection(default='monetary', selection=_get_available_carbon_compute_methods)


