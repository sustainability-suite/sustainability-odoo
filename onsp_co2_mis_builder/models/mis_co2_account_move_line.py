# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl


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
    ons_co2_currency_id = fields.Many2one(
        comodel_name="res.currency",
        # related="move_id.ons_co2_currency_id",
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
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
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
                    aml.date AS date,
                    aml.name AS name,
                    aml.move_id AS move_id,
                    aml.account_id AS account_id,
                    aml.journal_id AS journal_id,
                    aml.company_id AS company_id,
                    aml.partner_id AS partner_id,
                    am.carbon_currency_id AS ons_co2_currency_id,
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

class InstPeriodCO2(models.Model):
    _inherit = "mis.report.instance.period"
    
    def _get_additional_move_line_filter(self):
        domain = super(InstPeriodCO2, self)._get_additional_move_line_filter()
        if self._get_aml_model_name() == "mis.co2.account.move.line":
            domain.extend([("move_id.state", "!=", "cancel")])
        if (
            self._get_aml_model_name() == "mis.co2.account.move.line"
            and self.report_instance_id.target_move == "posted"
        ):
            domain.extend([("move_id.state", "=", "posted")])
        return domain
