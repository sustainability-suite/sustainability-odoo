from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    carbon_currency_label = fields.Char(related='company_id.carbon_currency_label')
    carbon_in_value = fields.Float(related='company_id.carbon_in_value', readonly=False)
    carbon_in_monetary_currency_id = fields.Many2one(related='company_id.carbon_in_monetary_currency_id', string="CO2e Currency for 'in' moves" )
    carbon_out_value = fields.Float(related='company_id.carbon_out_value', readonly=False)
    carbon_out_monetary_currency_id = fields.Many2one(related='company_id.carbon_out_monetary_currency_id', string="CO2e Currency for 'out' moves")
    invoice_report_footer = fields.Html(
        related='company_id.invoice_report_footer',
        readonly=False,
        translate=True,
    )
    carbon_lock_date = fields.Date(related='company_id.carbon_lock_date', readonly=False)
    carbon_default_data_uncertainty_value = fields.Float(related='company_id.carbon_default_data_uncertainty_value', readonly=False)

    available_module_names = fields.Char(compute="_compute_available_modules")
    extra_module_names = fields.Char(compute="_compute_available_modules")

    module_onsp_co2_purchase = fields.Boolean()
    module_onsp_co2_account_asset = fields.Boolean()
    module_onsp_co2_mis_builder = fields.Boolean()
    module_onsp_co2_account_asset_management = fields.Boolean()


    @api.depends('company_id')
    def _compute_available_modules(self):
        """
        These fields are used in attrs['invisible'] to know which options we should display in the settings
        It does not make sense to display options for modules that are not installable as the user will get an error

        Fields infos:
            available_module_names: comma separated list of modules that are available in the database
            extra_module_names: comma separated list of modules that are not available in the database
        """
        modules_names = {
            # Community
            'purchase',
            # Enterprise
            'account_asset',
            # OCA
            'mis_builder',
            'account_asset_management',
        }
        available_module_names = self.env['ir.module.module'].search([('name', 'in', list(modules_names))]).mapped('name')
        self.available_module_names = ','.join(available_module_names)
        self.extra_module_names = ', '.join(modules_names - set(available_module_names))

