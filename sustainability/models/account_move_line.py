from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line", "carbon.line.mixin"]

    carbon_balance = fields.Monetary(
        string="CO2 Balance",
        currency_field="carbon_currency_id",
        compute="_compute_carbon_balance",
        store=True,
    )
    carbon_debit = fields.Monetary(
        string="CO2 Debit",
        currency_field="carbon_currency_id",
        compute="_compute_carbon_debit_credit",
        store=True,
    )
    carbon_credit = fields.Monetary(
        string="CO2 Credit",
        currency_field="carbon_currency_id",
        compute="_compute_carbon_debit_credit",
        store=True,
    )

    carbon_is_date_locked = fields.Boolean(
        compute="_compute_carbon_is_date_locked", store=True
    )

    is_carbon_positive = fields.Boolean(
        compute="_compute_is_carbon_positive", store=False, readonly=True
    )

    carbon_supplier_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Supplier Info",
        compute="_compute_carbon_supplier_id",
    )

    is_invoice_line = fields.Boolean(default=False, compute="_compute_is_invoice_line")

    def _compute_is_invoice_line(self):
        for line in self:
            line.is_invoice_line = line.id in line.move_id.invoice_line_ids.ids

    def _compute_carbon_supplier_id(self):
        """
        Compute the carbon_supplier_id field.
        Note that since the same seller can be added multiple times to the same product,
        we need to filter the sellers by the partner_id of the order.
        If there are multiple matches,
        we'll take the most recent one.
        """

        for line in self:
            seller = line.product_id.seller_ids.filtered(
                lambda s: s.partner_id.id == line.move_id.partner_id.id  # noqa: B023
            )
            line.carbon_supplier_id = seller[-1] if len(seller) > 1 else seller

    def _prepare_analytic_distribution_line(
        self, distribution, account_id, distribution_on_each_plan
    ) -> dict:
        """I removed _prepare_analytic_line() (which is renamed in v16) because it calls this actual method to do the job"""
        res = super()._prepare_analytic_distribution_line(
            distribution, account_id, distribution_on_each_plan
        )

        # Using the same sign as carbon balance
        carbon_debt = self.carbon_debt * distribution / 100.0
        res["carbon_debt"] = carbon_debt if self.is_carbon_positive else -carbon_debt
        return res

    """ These methods might seem useless but the logic could change in the future so it's better to have them """

    def is_debit(self) -> bool:
        self.ensure_one()
        return bool(self.debit)

    def is_credit(self) -> bool:
        self.ensure_one()
        return bool(self.credit)

    def _compute_is_carbon_positive(self):
        for line in self:
            line.is_carbon_positive = line.carbon_balance >= 0

    # --------------------------------------------
    #                   COMPUTE
    # --------------------------------------------

    @api.depends("carbon_debit", "carbon_credit")
    def _compute_carbon_balance(self):
        for line in self:
            line.carbon_balance = line.carbon_debit - line.carbon_credit

    @api.depends("carbon_debt", "credit", "debit")
    def _compute_carbon_debit_credit(self):
        for line in self:
            credit = 0.0
            debit = 0.0
            # Weird if/elif statement, but we need that order of priority
            if line.move_id.is_inbound(include_receipts=True):
                credit = line.carbon_debt
            elif line.move_id.is_outbound(include_receipts=True):
                debit = line.carbon_debt
            elif line.credit != 0:
                credit = line.carbon_debt
            elif line.debit != 0:
                debit = line.carbon_debt

            line.carbon_credit = credit
            line.carbon_debit = debit

    @api.depends("company_id.carbon_lock_date", "move_id.date")
    def _compute_carbon_is_date_locked(self):
        for line in self:
            line.carbon_is_date_locked = line.company_id.carbon_lock_date and (
                line.move_id.date < line.company_id.carbon_lock_date
            )

    # --------------------------------------------
    #                   MIXIN
    # --------------------------------------------

    @api.depends(
        "product_id",
        "partner_id",
        "quantity",
        "credit",
        "debit",
        "move_type",
        "invoice_date",
        "carbon_data_uncertainty_percentage",
    )
    def _compute_carbon_debt(self, force_compute: bool | str | list[str] = None):
        return super()._compute_carbon_debt(force_compute)

    def _get_lines_to_compute_domain(self, force_compute: list[str]):
        domain = super()._get_lines_to_compute_domain(force_compute)
        domain.append(("carbon_is_date_locked", "=", False))
        domain.append(("display_type", "not in", ["line_section", "line_note"]))
        return domain

    # --- Methods to override ---

    @api.model
    def _get_states_to_auto_recompute(self) -> list[str]:
        return ["draft"]

    @api.model
    def _get_state_field_name(self) -> str:
        return "parent_state"

    @api.model
    def _get_carbon_compute_possible_fields(self) -> list[str]:
        return ["carbon_supplier_id", "product_id", "partner_id", "account_id"]

    # --- Partner ---
    def can_use_partner_id_carbon_value(self) -> bool:
        self.ensure_one()
        return self.move_id.is_outbound(include_receipts=True) and (
            self.partner_id and self.partner_id.can_compute_carbon_value("in")
        )

    # --- Supplier ---
    def can_use_carbon_supplier_id_carbon_value(self) -> bool:
        self.ensure_one()
        return bool(
            self.carbon_supplier_id
        ) and self.carbon_supplier_id.can_compute_carbon_value("in")

    def get_carbon_supplier_id_carbon_compute_values(self) -> dict:
        self.ensure_one()
        return self.get_product_id_carbon_compute_values()

    def _get_carbon_move_type(self) -> str:
        self.ensure_one()
        return (
            "out"
            if self.move_id.move_type in ["out_invoice", "out_refund", "out_receipt"]
            else "in"
        )

    def _get_carbon_compute_kwargs(self) -> dict:
        res = super()._get_carbon_compute_kwargs()
        res.update(
            {
                "carbon_type": self._get_carbon_move_type(),
                "date": self.move_id.date or self.move_id.invoice_date,
                # We take the company currency because credit/debit are expressed in that currency
                "from_currency_id": (
                    self.move_id.company_id or self.env.company
                ).currency_id,
                "reference": self.move_id.mapped("name"),
            }
        )
        return res

    def _get_line_amount(self) -> float:
        self.ensure_one()
        amount = (self.debit if self.is_debit() else self.credit) or 0.0
        # We don't take discounts into account for carbon values, so we need to reverse it
        # There is a very special case if the discount is exactly 100% (division by 0) so we have to get a value somehow with price_unit*quantity
        if self.discount:
            amount = (
                amount / (1 - self.discount / 100)
                if self.discount != 100
                else self.price_unit * self.quantity
            )
        return amount

    def _get_carbon_compute_default_record(self):
        self.ensure_one()
        return self.move_id.company_id

    def get_carbon_sign(self) -> int:
        self.ensure_one()
        return -1 if self.carbon_balance < 0 else 1

    # --- Modular methods ---
    # --- ACCOUNT ---

    def can_use_account_id_carbon_value(self) -> bool:
        self.ensure_one()
        return self.account_id.can_compute_carbon_value("in")

    def get_account_id_carbon_compute_values(self) -> dict:
        self.ensure_one()
        return {"carbon_type": "in"}

    # --- PRODUCT ---
    def can_use_product_id_carbon_value(self) -> bool:
        self.ensure_one()
        return bool(self.product_id) and (
            (  # Customer Invoice
                self.move_id.move_type in ["in_invoice", "in_receipt"]
                and self.product_id.can_compute_carbon_value("in")
            )
            or (  # Customer Credit Note
                self.move_id.move_type in ["out_refund"]
                and self.product_id.can_compute_carbon_value("out")
            )
            or (  # Vendor Bill
                self.move_id.move_type in ["out_invoice", "out_receipt"]
                and self.product_id.can_compute_carbon_value("out")
            )
            or (  # Vendor Credit Note
                self.move_id.move_type in ["in_refund"]
                and self.product_id.can_compute_carbon_value("in")
            )
        )

    def get_product_id_carbon_compute_values(self) -> dict:
        self.ensure_one()
        return {
            "quantity": self.quantity,
            "from_uom_id": self.product_uom_id,
            "product_id": self.product_id,
        }

    def action_recompute_carbon(self) -> dict:
        res = super().action_recompute_carbon()

        self.action_recompute_analytic_line()

        return res

    def action_recompute_analytic_line(self):
        """
        This method is used in the account move server action in order to recompute Co2.
        Here we delete the analytic line and then recreate them.
        I didn't find something that already does that.
        This method is multi.
        """
        self.analytic_line_ids.unlink()
        self._create_analytic_lines()
