from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

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
