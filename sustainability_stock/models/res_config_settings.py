from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    carbon_freight_product_upstream = fields.Many2one(
        string="Product for Upstream Freight",
        related="company_id.carbon_freight_product_upstream",
        readonly=False,
        domain=lambda self: [
            ("uom_id.category_id", "=", self.env.ref("uom.product_uom_categ_kgm").id)
        ],
    )
    carbon_freight_product_downstream = fields.Many2one(
        string="Product for Downstream Freight",
        related="company_id.carbon_freight_product_downstream",
        readonly=False,
        domain=lambda self: [
            ("uom_id.category_id", "=", self.env.ref("uom.product_uom_categ_kgm").id)
        ],
    )
    carbon_freight_climatiq_api_url = fields.Char(
        related="company_id.carbon_freight_climatiq_api_url",
        readonly=False,
        string="Climatiq API URL",
        help="API URL for accessing Climatiq services.",
    )
    carbon_freight_climatiq_api_key = fields.Char(
        related="company_id.carbon_freight_climatiq_api_key",
        readonly=False,
        string="Climatiq API Key",
        help="API key for accessing Climatiq services.",
    )
    carbon_freight_max_delivery_count = fields.Integer(
        related="company_id.carbon_freight_max_delivery_count",
        readonly=False,
        string="Max Deliveries to Process",
        help="Specify the maximum number of deliveries to process at once.",
    )
    carbon_freight_transport_mode = fields.Selection(
        related="company_id.carbon_freight_transport_mode",
        readonly=False,
        string="Default Transport Mode",
        help="Select the default mode of transportation for freight orders.",
    )
    carbon_freight_journal_id = fields.Many2one(
        "account.journal",
        related="company_id.carbon_freight_journal_id",
        string="Carbon Freight Journal",
        readonly=False,
    )
    carbon_freight_account_id = fields.Many2one(
        "account.account",
        related="company_id.carbon_freight_account_id",
        string="Carbon Freight Account",
        readonly=False,
    )
    carbon_freight_uncertainty_percentage = fields.Float(
        string="Carbon Uncertainty Percentage",
        related="company_id.carbon_freight_uncertainty_percentage",
        readonly=False,
    )
    carbon_freight_tolerance = fields.Integer(
        string="Tolerance",
        related="company_id.carbon_freight_tolerance",
        readonly=False,
    )
