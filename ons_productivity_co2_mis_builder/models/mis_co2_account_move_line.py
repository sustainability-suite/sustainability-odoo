# © 2021 Open Net Sarl

from odoo import fields, models, tools


class MisAccountCO2Line(models.Model):
    _name = "mis.co2.account.move.line"
    _auto = False
    _description = "MIS CO2 Account Line"

    date = fields.Date()
    move_line_id = fields.Many2one(
        string="Journal Items",
        comodel_name="account.move.line",
        help="The journal item of this CO2 entry line."
    )
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry',
        related="move_line_id.move_id",
        readonly=True,
        help="The journal entry of this CO2 entry line."
    )
    ons_co2_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="move_id.ons_co2_currency_id",
        readonly=True,
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
    )
    balance = fields.Monetary(
        string="CO2 Balance (Kg)",
        currency_field="ons_co2_currency_id",
    )
    debit = fields.Monetary(
        string="CO2 Debit (Kg)",
        currency_field="ons_co2_currency_id",
    )
    credit = fields.Monetary(
        string="CO2 Credit (Kg)",
        currency_field="ons_co2_currency_id",
    )
    state = fields.Selection(
        [("draft", "Unposted"), ("posted", "Posted")],
        string="Status",
    )

    def init(self):
        tools.drop_view_if_exists(self._cr, "mis_co2_account_move_line")
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW mis_co2_account_move_line AS (
                SELECT
                    aml.id AS id,
                    aml.id AS move_line_id,
                    aml.date as date,
                    aml.account_id as account_id,
                    aml.company_id as company_id,
                    'posted'::VARCHAR as state,
                    aml.ons_carbon_debit as debit,
                    aml.ons_carbon_credit as credit,
                    aml.ons_carbon_balance as balance
                FROM
                    account_move_line aml
            )"""
        )
