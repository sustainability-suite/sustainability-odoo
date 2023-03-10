from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"


    carbon_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref("onsp_co2.carbon_kilo", False),
    )

    carbon_debt = fields.Monetary(
        string="CO2 Debt (Kg)",
        compute="_compute_carbon_debt",
        store=True,
        currency_field='carbon_currency_id',
    )

    @api.depends("invoice_line_ids.carbon_balance")  # , "invoice_line_ids.ons_carbon_debt"
    def _compute_carbon_debt(self):
        for move in self:
            move.carbon_debt = sum(move.invoice_line_ids.mapped("carbon_balance"))
