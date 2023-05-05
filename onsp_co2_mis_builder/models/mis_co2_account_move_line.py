# -*- coding: utf-8 -*-
from odoo import fields, models, tools


class MisAccountCO2Line(models.Model):
    _name = "mis.co2.account.move.line"
    _auto = False
    _description = "MIS CO2 Account Line"

    date = fields.Date()
    name = fields.Char(
        string="Label",
    )
    move_line_id = fields.Many2one(
        string="Journal Items",
        comodel_name="account.move.line",
        help="The journal item of this CO2 entry line.",
    )
    journal_id = fields.Many2one(related="move_line_id.journal_id")
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry',
        help="The journal entry of this CO2 entry line.",
    )
    carbon_currency_id = fields.Many2one(
        'res.currency',
        compute="_compute_carbon_currency_id",
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
    )
    balance = fields.Monetary(
        string="CO2 Balance (Kg)",
        currency_field="carbon_currency_id",
    )
    debit = fields.Monetary(
        string="CO2 Debit (Kg)",
        currency_field="carbon_currency_id",
    )
    credit = fields.Monetary(
        string="CO2 Credit (Kg)",
        currency_field="carbon_currency_id",
    )
    state = fields.Selection(
        [("draft", "Unposted"), ("posted", "Posted")],
        string="Status",
    )

    def _compute_carbon_currency_id(self):
        for line in self:
            line.carbon_currency_id = self.env.ref("onsp_co2.carbon_kilo", raise_if_not_found=False)

    def init(self):
        tools.drop_view_if_exists(self._cr, "mis_co2_account_move_line")
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW mis_co2_account_move_line AS (
                SELECT
                    aml.id AS id,
                    aml.id AS move_line_id,
                    aml.date AS date,
                    aml.name AS name,
                    aml.move_id AS move_id,
                    aml.account_id AS account_id,
                    aml.journal_id AS journal_id,
                    aml.company_id AS company_id,
                    aml.partner_id AS partner_id,
                    'posted'::VARCHAR AS state,
                    aml.carbon_debit AS debit,
                    aml.carbon_credit AS credit,
                    aml.carbon_balance AS balance
                FROM
                    account_move_line AS aml
                INNER JOIN account_move AS am ON
                    am.id = aml.move_id
            )"""
        )


