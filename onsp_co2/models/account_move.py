from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"


    carbon_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref("onsp_co2.carbon_kilo", False),
    )
    carbon_balance = fields.Monetary(
        string="CO2 Equivalent",
        compute="_compute_carbon_balance",
        store=True,
        currency_field='carbon_currency_id',
        tracking=True,
    )

    @api.depends("invoice_line_ids.carbon_balance")
    def _compute_carbon_balance(self):
        for move in self:
            move.carbon_balance = abs(sum(move.invoice_line_ids.mapped("carbon_balance")))

    def action_recompute_carbon(self):
        """ Force re-computation of carbon values for lines. Todo: add a confirm dialog if a subset is 'posted' """
        for move in self:
            move.line_ids._compute_carbon_debt(force_compute=True)
