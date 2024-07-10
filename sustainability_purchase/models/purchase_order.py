from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    carbon_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_carbon_currency_id",
    )
    carbon_debt = fields.Monetary(
        string="CO2",
        compute="_compute_carbon_debt",
        store=True,
        currency_field="carbon_currency_id",
    )

    def _compute_carbon_currency_id(self):
        for order in self:
            order.carbon_currency_id = self.env.ref(
                "sustainability.carbon_kilo", raise_if_not_found=False
            )

    @api.depends("order_line.carbon_debt")
    def _compute_carbon_debt(self):
        for po in self:
            po.carbon_debt = sum(po.order_line.mapped("carbon_debt"))

    # Todo: put in a new mixin maybe? for model with a line_ids field that inherit from carbon.line.mixin (overkill imo)
    def action_recompute_carbon(self) -> dict:
        """Force re-computation of carbon values for PO lines."""
        for order in self:
            order.order_line.action_recompute_carbon()
        return {}
