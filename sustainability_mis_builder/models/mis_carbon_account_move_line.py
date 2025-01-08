from odoo import fields, models, tools


class MisCarbonAccountMoveLine(models.Model):
    _name = "mis.carbon.account.move.line"
    _auto = False
    _description = "MIS Carbon Account Line"

    date = fields.Date()
    name = fields.Char(
        string="Label",
    )
    move_line_id = fields.Many2one(
        string="Journal Items",
        comodel_name="account.move.line",
        help="The journal item of this carbon line.",
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
        help="The journal of this carbon line.",
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Journal Entry",
        help="The journal entry of this carbon line.",
    )
    carbon_currency_id = fields.Many2one(
        "res.currency",
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
        currency_field="carbon_currency_id",
    )
    debit = fields.Monetary(
        currency_field="carbon_currency_id",
    )
    credit = fields.Monetary(
        currency_field="carbon_currency_id",
    )
    parent_state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
    )

    def _compute_carbon_currency_id(self):
        for line in self:
            line.carbon_currency_id = self.env.ref(
                "sustainability.carbon_kilo", raise_if_not_found=False
            )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "mis_carbon_account_move_line")
        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW mis_carbon_account_move_line AS (
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
                    am.state AS parent_state,
                    aml.carbon_debit AS debit,
                    aml.carbon_credit AS credit,
                    aml.carbon_balance AS balance
                FROM
                    account_move_line AS aml
                INNER JOIN account_move AS am ON
                    am.id = aml.move_id
            )"""
        )
