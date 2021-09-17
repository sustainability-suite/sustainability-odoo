# -*- coding: utf-8 -*-
# © 2020 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class AccountingCo2FinancialReport(models.Model):
    _inherit = "account.financial.html.report"

    ons_is_co2_report = fields.Boolean(
        string="Is it a Co2 Report ?",
        help="Enable this field to show co2 balance in financial report",
    )

    # BLG: Co2 currency used in financial report
    ons_carbon_monetary_currency = fields.Many2one(
        "res.currency",
        string="Co2 Unit",
        help="Currency used in co2 financial report",
    )

    @api.model
    def _format_cell_value(
        self, financial_line, amount, currency=False, blank_if_zero=False
    ):
        """Format the value to display inside a cell depending the 'figure_type' field in the financial report line.
        :param financial_line:  An account.financial.html.report.line record.
        :param amount:          A number.
        :param currency:        An optional res.currency record.
        :param blank_if_zero:   An optional flag forcing the string to be empty if amount is zero.
        :return:
        """
        if not financial_line.formulas:
            return ""

        if self._context.get("no_format"):
            return amount

        if not self.ons_is_co2_report:
            if financial_line.figure_type == "float":
                return super().format_value(
                    amount, currency=currency, blank_if_zero=blank_if_zero
                )
            elif financial_line.figure_type == "percents":
                return str(round(amount * 100, 1)) + "%"
            elif financial_line.figure_type == "no_unit":
                return round(amount, 1)
        # BLG: Overrides currency when co2 reporting
        if self.ons_is_co2_report:
            return super().format_value(
                amount,
                currency=self.ons_carbon_monetary_currency,
                blank_if_zero=blank_if_zero,
            )
        return amount