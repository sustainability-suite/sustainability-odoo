from odoo import _, api, fields, models


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

    @api.model
    def _carbon_get_other_fields(cls):
        res = super()._carbon_get_other_fields()
        res.append(
            dict(
                name="carbon_freight_transport_mode",
                string=_("Transport Mode"),
                group_name="group_carbon_freight_settings",
                group_string=_("CLimatiq API"),
            ),
        )
        return res
