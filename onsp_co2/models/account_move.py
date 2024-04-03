from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

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
                "onsp_co2.carbon_kilo", raise_if_not_found=False
            )

    @api.depends("invoice_line_ids.carbon_balance")
    def _compute_carbon_balance(self):
        for move in self:
            move.carbon_balance = abs(
                sum(move.invoice_line_ids.mapped("carbon_balance"))
            )

    @api.depends("invoice_line_ids.carbon_uncertainty_value")
    def _compute_carbon_uncertainty_value(self):
        for move in self:
            move.carbon_uncertainty_value = abs(
                sum(move.invoice_line_ids.mapped("carbon_uncertainty_value"))
            )

    def action_recompute_carbon_confirm(self):
        # Todo: if a subset is 'posted'
        wizard = self.env["carbon.confirm.dialog"].create(
            dict(
                message=_(
                    "Are you sure you want to continue ? By doing so you may make changes that wasn't supposed to happen. DO IT AT YOU'RE OWN RISK"
                )
            )
        )
        return {
            "name": "Warning",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "carbon.confirm.dialog",
            "res_id": wizard.id,
            "target": "new",
            "context": {
                "model": "account.move",
                "ids": self.ids,
                "fname": "action_recompute_carbon",
                **self.env.context,
            },
        }

    def action_recompute_carbon(self) -> dict:
        """Force re-computation of carbon values for lines."""
        for move in self:
            move.line_ids.action_recompute_carbon()
        return {}
