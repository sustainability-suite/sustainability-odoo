from odoo import fields, models


class CarbonLineOrigin(models.Model):
    _inherit = "carbon.line.origin"

    move_carbon_freight_picking_id = fields.Many2one(
        related="move_id.carbon_freight_picking_id", store=True
    )
