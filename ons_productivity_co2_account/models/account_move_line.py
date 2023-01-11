# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_ons_carbon_debt(self):
        for line in self:
            computed_cost = abs(
                line.price_subtotal
                or line.credit
                or line.debit
                or (
                    line.quantity
                    * line.price_unit
                    * (100.0 - line.discount)
                    / 100.0
                )
            )

            if (
                not line.product_id and
                line.account_id and
                line.account_id.ons_use_co2_ratio
            ):
                return computed_cost * line.account_id.ons_carbon_ratio
                
            if line.credit:
                return line.product_id.ons_get_carbon_credit(
                    line.quantity,
                    cost=computed_cost,
                )
            elif line.debit:
                return line.product_id.ons_get_carbon_debit(
                    line.quantity,
                    cost=computed_cost,
                )
        return 0

    ons_co2_currency_id = fields.Many2one(
        "res.currency",
        related="move_id.ons_co2_currency_id",
        readonly=True,
    )

    # Related field used to display account_user_type in account.move.line's view
    ons_account_user_type = fields.Selection(
        string="Type",
        related="account_id.account_type",
        store=True,
    )

    ons_carbon_debt = fields.Monetary(
        string="CO2 Debt (Kg)",
        currency_field="ons_co2_currency_id",
        help="A positive value means that your system's debt grows, a negative value means it shrinks",
        default=lambda line: line._get_ons_carbon_debt(),
    )

    ons_carbon_balance = fields.Monetary(
        string="CO2 Balance (Kg)",
        store=True,
        compute="_compute_ons_carbon_balance",
        currency_field="ons_co2_currency_id",
    )

    ons_carbon_debit = fields.Monetary(
        string="CO2 Debit (Kg)",
        currency_field="ons_co2_currency_id",
    )

    ons_carbon_credit = fields.Monetary(
        string="CO2 Credit (Kg)",
        currency_field="ons_co2_currency_id",
    )

    def _prepare_analytic_line(self):
        res = super(AccountMoveLine, self)._prepare_analytic_line()
        for data in res:
            move_line_id = self.browse(data["move_id"])
            data["ons_carbon_debt"] = move_line_id.ons_carbon_balance
        return res

    def _prepare_analytic_distribution_line(self, distribution, account_id, distribution_on_each_plan):
        res = super(AccountMoveLine, self)._prepare_analytic_distribution_line(
            distribution, account_id, distribution_on_each_plan
        )
        res["ons_carbon_debt"] = (
            -self.ons_carbon_balance * distribution / 100.0
        )
        return res

    @api.onchange('ons_carbon_debt')
    def _ons_co2_onchange_ons_carbon_debt(self):
        for line in self:
            line.update(line._get_fields_onchange_ons_carbon_debt(
                ons_carbon_debt=self.ons_carbon_debt,
            ))

    @api.depends("ons_carbon_debit", "ons_carbon_credit")
    def _compute_ons_carbon_balance(self):
        for line in self:
            line.ons_carbon_balance = line.ons_carbon_debit - line.ons_carbon_credit

    @api.onchange("ons_carbon_debit")
    def _onchange_ons_carbon_debit(self):
        if self.ons_carbon_debit:
            vals = self._get_fields_onchange_ons_carbon_debt(
                ons_carbon_debit=self.ons_carbon_debit
            )
            self.update(vals)

    @api.onchange("ons_carbon_credit")
    def _onchange_ons_carbon_credit(self):
        if self.ons_carbon_credit:
            vals = self._get_fields_onchange_ons_carbon_debt(
                ons_carbon_credit=self.ons_carbon_credit
            )
            self.update(vals)

    @api.onchange("product_id", "quantity", "price_subtotal")
    def _set_ons_carbon_debt(self):
        for line in self:
            ons_carbon_debt = line._get_ons_carbon_debt()
            line.ons_carbon_debt = ons_carbon_debt

    def _get_fields_onchange_ons_carbon_debt(
        self,
        ons_carbon_debt=None,
        ons_carbon_debit=None,
        ons_carbon_credit=None,
        move_type=None,
        **kw
    ):
        """Based on methods _get_fields_onchange_subtotal and _get_fields_onchange_subtotal_model"""
        self.ensure_one()

        # Handle case where ons_carbon_debit or ons_carbon_credit is defined
        if ons_carbon_debit is not None and not ons_carbon_credit:
            # If debit is 0, do not change credit's value
            ons_carbon_credit = (
                0 if ons_carbon_debit else self.ons_carbon_credit
            )
        elif not ons_carbon_debit and ons_carbon_credit is not None:
            # If credit is 0, do not change debit's value
            ons_carbon_debit = (
                0 if ons_carbon_credit else self.ons_carbon_debit
            )
        elif ons_carbon_debit and ons_carbon_credit:
            # Both can not be non 0 values
            raise ValidationError(
                "ons_carbon_debit and ons_carbon_credit are both defined"
            )
        
        if ons_carbon_debit or ons_carbon_credit:
            ons_carbon_debt = ons_carbon_debit or ons_carbon_credit
            data = {
                "ons_carbon_debt": ons_carbon_debt,
                "ons_carbon_balance": ons_carbon_debit - ons_carbon_credit,
                "ons_carbon_debit": ons_carbon_debt if ons_carbon_debit else 0,
                "ons_carbon_credit": 0 if ons_carbon_debit else ons_carbon_debt,
            }
            return data
        
        # No Value provided => sent current values
        if ons_carbon_debt is None:
            data = {
                "ons_carbon_debt": self.ons_carbon_debt,
                "ons_carbon_balance": self.ons_carbon_balance,
                "ons_carbon_debit": self.ons_carbon_debit,
                "ons_carbon_credit": self.ons_carbon_credit,
            }
            return data
        # Only ons_carbon_debt provided
        if self.debit:
            sign = 1
        elif self.credit:
            sign = -1
        else:
            move_type = move_type or self.move_id.move_type
            if move_type in self.move_id.get_inbound_types():
                sign = -1
            else:
                sign = 1

        balance = ons_carbon_debt * sign
        
        data = {
            "ons_carbon_debt": ons_carbon_debt,
            "ons_carbon_balance": balance,
            "ons_carbon_debit": sign > 0 and balance or 0.0,
            "ons_carbon_credit": sign < 0 and -balance or 0.0,
        }
        return data

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)
        carbon_keys = (
            "ons_carbon_debt", "ons_carbon_debit", "ons_carbon_credit"
        )
        for line, vals in zip(res, vals_list):
            if not any(
                key in vals
                for key in carbon_keys
            ):
                line._set_ons_carbon_debt()
            line.update(line._get_fields_onchange_ons_carbon_debt(**vals))
        res.mapped("product_id")._compute_ons_carbon_debt()
        return res

    def write(self, vals):
        if not any(
            key in vals
            for key in ["ons_carbon_debt", "ons_carbon_debit", "ons_carbon_credit"]
        ):
            return super(AccountMoveLine, self).write(vals)

        res = True
        for line in self:
            update = line._get_fields_onchange_ons_carbon_debt(**vals)
            to_write = {**update, **vals}
            res |= super(AccountMoveLine, line).write(to_write)
        self.mapped("product_id")._compute_ons_carbon_debt()
        return res

    # Voir la méthode
    # _move_autocomplete_invoice_lines_create
    # _move_autocomplete_invoice_lines_values
    # _onchange_price_subtotal
    # _get_fields_onchange_subtotal_model
