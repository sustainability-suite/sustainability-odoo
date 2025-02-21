from odoo import api, fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "carbon.common.mixin"]

    carbon_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_carbon_currency_id",
    )
    carbon_balance = fields.Monetary(
        string="CO2 Equivalent",
        compute="_compute_carbon_balance",
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

    def _compute_carbon_currency_id(self):
        for move in self:
            move.carbon_currency_id = self.env.ref(
                "sustainability.carbon_kilo", raise_if_not_found=False
            )

    @api.depends("invoice_line_ids.carbon_balance")
    def _compute_carbon_balance(self):
        for move in self:
            move.carbon_balance = sum(move.invoice_line_ids.mapped("carbon_balance"))

    @api.depends("invoice_line_ids.carbon_uncertainty_value")
    def _compute_carbon_uncertainty_value(self):
        for move in self:
            sum_uncertainty = sum(
                move.invoice_line_ids.mapped("carbon_uncertainty_value")
            )
            move.carbon_uncertainty_value = (
                -sum_uncertainty if move.carbon_balance < 0 else sum_uncertainty
            )

    def action_recompute_carbon(self) -> dict:
        """Force re-computation of carbon values for lines"""
        return self.line_ids.action_recompute_carbon()

    # Carbon Line Origin Smart Button
    @api.model
    def _carbon_get_line_field(cls):
        return "line_ids"
