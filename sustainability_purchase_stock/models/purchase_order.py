from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "carbon.common.mixin"]

    sustainability_partner_shipping_id = fields.Many2one(
        "res.partner",
        string="Delivery Address",
    )

    def _prepare_picking(self):
        """Override to include delivery address in picking preparation."""
        res = super()._prepare_picking()
        if self.sustainability_partner_shipping_id:
            res.update(
                {
                    "partner_id": self.sustainability_partner_shipping_id.id,
                }
            )
        return res

    @api.onchange("partner_id")
    def _onchange_partner_id_set_sustainability_shipping(self):
        for order in self:
            if not order.partner_id:
                continue
            addresses = order.partner_id.address_get(["delivery"])
            delivery_partner_id = addresses.get("delivery")
            order.sustainability_partner_shipping_id = (
                delivery_partner_id or order.partner_id.id
            )
