from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    carbon_currency_id = fields.Many2one(related="order_id.carbon_currency_id")
    carbon_debt = fields.Monetary(
        string="CO2 Debt",
        currency_field="carbon_currency_id",
        help="A positive value means that your system's debt grows, a negative value means it shrinks",
        compute="_compute_carbon_debt",
        readonly=False,
        store=True,
    )

    @api.depends('product_id.carbon_value', 'product_qty')
    def _compute_carbon_debt(self):
        for line in self:
            line.carbon_debt = line.product_qty * line.product_id.carbon_value

    def _prepare_account_move_line(self, move=False):
        """ Somehow this works and does not seem to re-compute co2 values after line creation """
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        res["carbon_debt"] = self.qty_to_invoice * self.product_id.carbon_value
        res["carbon_value_origin"] = _("Purchase Order %s", self.order_id.name)
        return res
