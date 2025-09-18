from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "carbon.common.mixin"]

    carbon_debt = fields.Monetary(
        string="CO2 Equivalent",
        compute="_compute_carbon_debt",
        store=True,
        currency_field="carbon_currency_id",
        tracking=True,
    )
    carbon_uncertainty_value = fields.Monetary(
        string="CO2 Uncertainty",
        compute="_compute_carbon_uncertainty_value",
        store=True,
        currency_field="carbon_currency_id",
        tracking=True,
    )
    carbon_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_carbon_currency_id",
        store=True,
    )

    @api.depends("order_line.carbon_debt")
    def _compute_carbon_debt(self):
        for order in self:
            order.carbon_debt = sum(order.order_line.mapped("carbon_debt"))

    @api.depends("order_line.carbon_uncertainty_value")
    def _compute_carbon_uncertainty_value(self):
        for order in self:
            sum_uncertainty = sum(order.order_line.mapped("carbon_uncertainty_value"))
            order.carbon_uncertainty_value = (
                -sum_uncertainty if order.carbon_debt < 0 else sum_uncertainty
            )

    @api.depends("order_line.carbon_currency_id")
    def _compute_carbon_currency_id(self):
        for order in self:
            currencies = order.order_line.mapped("carbon_currency_id")
            unique_currencies = list(set(currencies))
            if len(unique_currencies) > 1:
                raise ValueError(
                    _("All order lines must have the same carbon currency.")
                )
            order.carbon_currency_id = (
                unique_currencies[0]
                if unique_currencies
                else order.company_id.currency_id
            )

    def action_recompute_carbon(self) -> dict:
        """Force re-computation of carbon values for PO lines."""
        for order in self:
            order.order_line.action_recompute_carbon()
        return {}

    # Carbon Line Origin Smart Button
    @api.model
    def _carbon_get_line_field(cls):
        return "order_line"
