from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"


    carbon_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref("onsp_co2.carbon_kilo", False),
    )
    carbon_debt = fields.Monetary(
        string="CO2 Debt",
        compute="_compute_carbon_debt",
        store=True,
        currency_field='carbon_currency_id',
        tracking=True,
    )

    @api.depends("invoice_line_ids.carbon_balance")
    def _compute_carbon_debt(self):
        for move in self:
            move.carbon_debt = sum(move.invoice_line_ids.mapped("carbon_balance"))

    def action_recompute_carbon(self):
        """ Force re-computation of carbon values for lines. Todo: add a confirm dialog if a subset is 'posted' """
        for move in self:
            move.line_ids._compute_carbon_debt(force_compute=True)
