from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    carbon_freight_picking_id = fields.Many2one(
        comodel_name="stock.picking", string="Stock Transfer"
    )
