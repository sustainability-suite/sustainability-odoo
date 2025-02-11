from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    carbon_freight_product_upstream = fields.Many2one(
        "product.product",
        string="Product for Upstream Freight",
    )
    carbon_freight_product_downstream = fields.Many2one(
        "product.product",
        string="Product for Downstream Freight",
    )
    carbon_freight_climatiq_api_url = fields.Char(
        help="API URL for accessing Climatiq services.",
    )
    carbon_freight_climatiq_api_key = fields.Char(
        help="API key for accessing Climatiq services.",
    )
    carbon_freight_max_delivery_count = fields.Integer(
        default=10,
        string="Max deliveries to process",
        help="Specify the maximum number of deliveries to process.",
    )
    carbon_freight_transport_mode = fields.Selection(
        [
            ("road", "Road"),
            ("air", "Air"),
            ("sea", "Sea"),
            ("rail", "Rail"),
        ],
        string="Default Transport Mode",
        help="Select the default mode of transportation for freight orders.",
    )
    carbon_freight_journal_id = fields.Many2one(
        "account.journal", string="Carbon Freight Journal"
    )
    carbon_freight_account_id = fields.Many2one(
        "account.account",
        string="Carbon Freight Account",
        domain="[('deprecated', '=', False)]",
    )
    carbon_freight_uncertainty_percentage = fields.Float(
        default=0.0, string="Uncertainty"
    )
