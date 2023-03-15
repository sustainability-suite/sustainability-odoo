from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    carbon_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref("onsp_co2.carbon_kilo", False),
    )
    carbon_debt = fields.Monetary(
        string="CO2 Debt",
        compute="_compute_carbon_debt",
        store=True,
        currency_field='carbon_currency_id',
    )

    @api.depends("order_line.carbon_debt")
    def _compute_carbon_debt(self):
        for po in self:
            po.carbon_debt = sum(po.order_line.mapped("carbon_debt"))

