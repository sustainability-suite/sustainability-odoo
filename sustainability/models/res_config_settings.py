from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    carbon_in_factor_id = fields.Many2one(
        string="Emission Factor Purchases",
        related="company_id.carbon_in_factor_id",
        readonly=False,
    )
    carbon_out_factor_id = fields.Many2one(
        string="Emission Factor Sales",
        related="company_id.carbon_out_factor_id",
        readonly=False,
    )
    carbon_allowed_factor_ids = fields.Many2many(
        related="company_id.carbon_allowed_factor_ids"
    )

    invoice_report_footer = fields.Html(
        related="company_id.invoice_report_footer",
        readonly=False,
        translate=True,
    )
    carbon_lock_date = fields.Date(
        related="company_id.carbon_lock_date", readonly=False
    )
    carbon_default_data_uncertainty_percentage = fields.Float(
        related="company_id.carbon_default_data_uncertainty_percentage", readonly=False
    )

    available_module_names = fields.Char(compute="_compute_available_modules")
    extra_module_names = fields.Char(compute="_compute_available_modules")

    module_sustainability_purchase = fields.Boolean()
    module_sustainability_account_asset = fields.Boolean()
    module_sustainability_mis_builder = fields.Boolean()
    module_sustainability_account_asset_management = fields.Boolean()
    module_sustainability_employee_commuting = fields.Boolean()
    module_sustainability_hr_expense_report = fields.Boolean()

    @api.depends("company_id")
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
            "purchase",
            "hr",
            # Enterprise
            "account_asset",
            # OCA
            "mis_builder",
            "account_asset_management",
            "hr_expense",
        }
        available_module_names = (
            self.env["ir.module.module"]
            .search([("name", "in", list(modules_names))])
            .mapped("name")
        )
        self.available_module_names = ",".join(available_module_names)
        self.extra_module_names = ", ".join(modules_names - set(available_module_names))
