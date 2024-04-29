from typing import List

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _confirm_dialog_methods: List[str] = ["action_recompute_carbon"]

    carbon_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_carbon_currency_id",
    )
    carbon_debt = fields.Monetary(
        string="CO2 Debt",
        compute="_compute_carbon_debt",
        store=True,
        currency_field="carbon_currency_id",
    )

    def _compute_carbon_currency_id(self):
        for order in self:
            order.carbon_currency_id = self.env.ref(
                "onsp_co2.carbon_kilo", raise_if_not_found=False
            )

    @api.depends("order_line.carbon_debt")
    def _compute_carbon_debt(self):
        for po in self:
            po.carbon_debt = sum(po.order_line.mapped("carbon_debt"))

    def action_recompute_carbon_confirm(self):
        # Todo: if a subset is 'posted'
        res_ids = ",".join([str(id) for id in self.ids])
        wizard = self.env["confirm.dialog"].create(
            dict(
                message=_(
                    "Are you sure you want to continue ? By doing so you may make changes that wasn't supposed to happen. DO IT AT YOU'RE OWN RISK"
                ),
                res_model=self._name,
                res_ids=res_ids,
                callback="action_recompute_carbon",
            )
        )

        return wizard.get_action()

    # Todo: put in a new mixin maybe? for model with a line_ids field that inherit from carbon.line.mixin (overkill imo)
    def action_recompute_carbon(self) -> dict:
        """Force re-computation of carbon values for PO lines."""
        for order in self:
            order.order_line.action_recompute_carbon()
        return {}
