from collections import defaultdict
from datetime import datetime

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError


class CarbonFactor(models.Model):
    _name = "carbon.factor"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "carbon.copy.mixin",
        "common.mixin",
    ]
    _description = "Carbon Emission Factor"
    _order = "name"
    _parent_store = True

    # Core and utils fields
    name = fields.Char(required=True, tracking=True)
    carbon_database_id = fields.Many2one(
        comodel_name="carbon.factor.database", tracking=True, string="Database"
    )
    carbon_contributor_id = fields.Many2one(
        comodel_name="carbon.factor.contributor", tracking=True, string="Contributor"
    )
    has_invalid_value = fields.Boolean(compute="_compute_has_invalid_value")
    carbon_compute_method = fields.Selection(
        selection=[("physical", "Physical"), ("monetary", "Monetary")],
        string="Compute method",
        tracking=True,
    )
    uncertainty_percentage = fields.Float(
        string="Uncertainty (%)", default=0.0, tracking=True, group_operator=False
    )
    active = fields.Boolean(default=True, tracking=True)
    country_id = fields.Many2one("res.country", string="Country", tracking=True)
    country_group_id = fields.Many2one(
        "res.country.group", string="Country Group", tracking=True
    )

    # Categories fields
    parent_id = fields.Many2one(
        comodel_name="carbon.factor",
        string="Parent",
        index=True,
        ondelete="restrict",
        tracking=True,
    )
    hierarchy = fields.Char(compute="_compute_hierarchy", recursive=True)
    category = fields.Char(compute="_compute_category", store=True)
    root = fields.Char(compute="_compute_root", store=True)
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many(comodel_name="carbon.factor", inverse_name="parent_id")
    child_qty = fields.Integer(compute="_compute_child_qty")
    descendant_ids = fields.Many2many(
        comodel_name="carbon.factor", compute="_compute_descendant_ids", recursive=True
    )

    # Values IDs fields
    ghg_view_mode = fields.Boolean(
        string="Show greenhouse gases detail",
        help="Toggle to show GHG details",
        tracking=True,
    )
    carbon_currency_id = fields.Many2one(
        comodel_name="res.currency", compute="_compute_carbon_currency_id"
    )
    carbon_currency_label = fields.Char(
        compute="_compute_carbon_currency_id", default="kgCO2e"
    )
    value_ids = fields.One2many(
        comodel_name="carbon.factor.value", inverse_name="factor_id", tracking=True
    )
    recent_value_id = fields.Many2one(
        comodel_name="carbon.factor.value", compute="_compute_recent_value", store=True
    )
    carbon_date = fields.Date(related="recent_value_id.date", store=True)

    carbon_value = fields.Float(
        compute="_compute_carbon_value", store=True, string="Value"
    )
    carbon_uom_id = fields.Many2one(related="recent_value_id.carbon_uom_id", store=True)
    carbon_monetary_currency_id = fields.Many2one(
        related="recent_value_id.carbon_monetary_currency_id"
    )
    unit_label = fields.Char(related="recent_value_id.unit_label")

    # Type fields
    required_type_ids = fields.Many2many("carbon.factor.type", string="Required Types")
    factor_value_type_id = fields.Many2one(
        related="recent_value_id.type_id", string="Factor Value Type", store=True
    )
    # Quantity fields for smart button

    chart_of_account_qty = fields.Integer(compute="_compute_chart_of_account_qty")
    product_qty = fields.Integer(compute="_compute_product_qty")
    product_categ_qty = fields.Integer(compute="_compute_product_categ_qty")
    account_move_qty = fields.Integer(compute="_compute_account_move_qty")

    # --------------------------------------------

    def _get_record_description(self) -> str:
        self.ensure_one()
        return self._description + (f": {self.name}" if hasattr(self, "name") else "")

    @api.constrains("country_id", "country_group_id")
    def _check_country_constraints(self):
        for record in self:
            if record.country_id and record.country_group_id:
                raise exceptions.ValidationError(
                    _(
                        "You can only select either a Country or a Country Group, not both."
                    )
                )

    # --------------------------------------------
    #                   COMPUTE
    # --------------------------------------------

    @api.depends("value_ids.date")
    def _compute_recent_value(self):
        for factor in self:
            value_with_dates = factor.value_ids.filtered("date")
            factor.recent_value_id = value_with_dates and max(
                value_with_dates, key=lambda f: f.date
            )

    @api.depends("value_ids.date")
    def _compute_carbon_value(self):
        for factor in self:
            value_with_dates = factor.value_ids.filtered("date")
            if value_with_dates:
                dates_values = {}
                for factor_value in value_with_dates:
                    dates_values[factor_value.date] = (
                        dates_values.get(factor_value.date, 0)
                        + factor_value.carbon_value
                    )
                most_recent_date = max(dates_values.keys())
                factor.carbon_value = dates_values[most_recent_date]
            else:
                factor.carbon_value = False

    @api.depends("child_ids")
    def _compute_child_qty(self):
        for factor in self:
            factor.child_qty = len(factor.child_ids)

    @api.depends("child_ids.descendant_ids")
    def _compute_descendant_ids(self):
        for factor in self:
            factor.descendant_ids = factor.child_ids | factor.child_ids.descendant_ids

    def _compute_chart_of_account_qty(self):
        count_data = self._get_count_by_model(model="account.account")
        for factor in self:
            factor.chart_of_account_qty = count_data.get(factor.id, 0)

    def _compute_account_move_qty(self):
        origins = self.env["carbon.line.origin"].read_group(
            [
                ("factor_id", "in", self.ids),
                ("res_model", "=", "account.move.line"),
                ("move_id", "!=", False),
            ],
            ["factor_id"],
            ["factor_id", "move_id"],
            lazy=False,
        )
        factor_to_move_qty = defaultdict(int)
        for origin in origins:
            factor_to_move_qty[origin["factor_id"][0]] += 1
        for factor in self:
            factor.account_move_qty = factor_to_move_qty.get(factor.id, 0)

    def _compute_product_qty(self):
        count_data = self._get_count_by_model(model="product.template")
        for factor in self:
            factor.product_qty = count_data.get(factor.id, 0)

    def _compute_product_categ_qty(self):
        count_data = self._get_count_by_model(model="product.category")
        for factor in self:
            factor.product_categ_qty = count_data.get(factor.id, 0)

    def _compute_carbon_currency_id(self):
        for factor in self:
            factor.carbon_currency_id = (
                self.env.ref("sustainability.carbon_kilo", raise_if_not_found=False)
                or self.env["res.currency"]
            )
            factor.carbon_currency_label = factor.carbon_currency_id.currency_unit_label

    @api.depends("parent_id.hierarchy", "name")
    def _compute_hierarchy(self):
        for factor in self:
            factor.hierarchy = (
                f"{factor.parent_id.hierarchy} > {factor.name}"
                if factor.parent_id
                else factor.name
            )

    @api.depends("hierarchy")
    def _compute_category(self):
        for factor in self:
            if factor.hierarchy:
                hierarchy_list = factor.hierarchy.split(" > ")
                hierarchy_list.pop()
                factor.category = " > ".join(hierarchy_list)
            else:
                factor.category = ""

    @api.depends("hierarchy")
    def _compute_root(self):
        for factor in self:
            if factor.hierarchy:
                hierarchy_list = factor.hierarchy.split(" > ")
                factor.root = hierarchy_list[0]
            else:
                factor.root = ""

    @api.depends(
        "carbon_compute_method", "carbon_monetary_currency_id", "carbon_uom_id"
    )
    def _compute_unit_label(self):
        for factor in self:
            if not factor.carbon_compute_method or not (
                factor.carbon_uom_id or factor.carbon_monetary_currency_id
            ):
                factor.unit_label = ""
            else:
                factor.unit_label = "/ " + (
                    factor.carbon_uom_id.name
                    or factor.carbon_monetary_currency_id.currency_unit_label
                )

    @api.depends(
        "carbon_compute_method",
        "value_ids.carbon_uom_id",
        "value_ids.carbon_monetary_currency_id",
    )
    def _compute_has_invalid_value(self):
        for factor in self:
            factor.has_invalid_value = (
                factor.carbon_compute_method == "physical"
                and not all([v.carbon_uom_id for v in factor.value_ids])
            ) or (
                factor.carbon_compute_method == "monetary"
                and not all([v.carbon_monetary_currency_id for v in factor.value_ids])
            )

    # --------------------------------------------
    #                   CHECKS
    # --------------------------------------------

    def check_distribution(
        self, distribution: dict["CarbonFactor", float]
    ) -> dict["CarbonFactor", float]:
        """
        Check that the distribution is valid and update it if needed
        """
        # Todo: make automatic distribution for any number of factors
        if not distribution and len(self) == 1:
            return {self: 1.0}

        total_distribution = sum(distribution.values())
        if total_distribution != 1:
            raise ValidationError(
                _(
                    "Distribution values must sum up to 1 (current value: %s)",
                    total_distribution,
                )
            )
        if not all([factor in distribution for factor in self]):
            raise ValidationError(
                _(
                    "Some factors are missing in distribution (ids: %s)",
                    set(self.ids) - set(distribution.keys()),
                )
            )
        if len(distribution) != len(self):
            raise ValidationError(
                _(
                    "The factor count is different from the distribution keys count (factor count: %s, keys count: %s)",
                    len(self),
                    len(distribution),
                )
            )

        return distribution

    def _check_required_types(self):
        """
        Validates the type ID of the carbon factor.

        This method ensures that all required types are present for each date in the value_ids field.
        If a required type is missing, it raises a ValidationError.

        Raises:
            ValidationError: If a required type is missing for a specific date.
        """
        self.ensure_one()

        date_to_values = defaultdict(lambda: self.env["carbon.factor.value"])
        for value in self.value_ids:
            date_to_values[str(value.date)] |= value

        for date, value_list in date_to_values.items():
            if self.required_type_ids - value_list.type_id:
                raise ValidationError(
                    _(
                        "Please enter all the required type for the following date (%s)",
                        date,
                    )
                )

    # --------------------------------------------
    #                   CRUD
    # --------------------------------------------

    def write(self, vals):
        if (
            vals.get("carbon_compute_method") == "physical"
            and not all([v.carbon_uom_id for v in self.value_ids])
        ) or (
            vals.get("carbon_compute_method") == "monetary"
            and not all([v.carbon_monetary_currency_id for v in self.value_ids])
        ):
            raise ValidationError(
                _(
                    "You can not change the compute method if some values miss currency/unit of measure"
                )
            )
        res = super().write(vals)
        for factor in self:
            factor._check_required_types()
        return res

    # --------------------------------------------
    #                 MISC METHODS
    # --------------------------------------------

    def _get_values_at_date(self, date=None):
        """Return"""
        self.ensure_one()
        if not self.value_ids:
            raise ValidationError(
                _(
                    "_get_values_at_date: No value found for the following factor: %s",
                    self.name,
                )
            )
        if not date:
            date = fields.Date.today()
        if isinstance(date, datetime):
            date = date.date()

        values_before_date = self.value_ids.filtered(lambda v: v.date <= date)
        closest_date = (
            max(values_before_date.mapped("date"))
            if values_before_date
            else min(self.value_ids.mapped("date"))
        )
        return self.value_ids.filtered(lambda v: v.date == closest_date)

    def _get_count_by_model(self, model: str) -> dict:
        """
        Compute the total count of carbon factors for a given model.

        This function reads data from distribution lines associated with given model,
        and then calculates the total count of carbon factors for each item in the data.

        Args:
            model (str, optional): The name of the model to compute the carbon factors count for.

        Returns:
            dict: A dictionary where keys are factor ids and values are the total count of `model` for that id.
        """
        distribution_lines = self.env["carbon.distribution.line"].read_group(
            [("res_model", "=", model), ("factor_id", "in", self.ids)],
            ["factor_id"],
            ["factor_id"],
        )
        total_count = defaultdict(int)
        for line in distribution_lines:
            total_count[line["factor_id"][0]] += line["factor_id_count"]

        return total_count

    # --------------------------------------------
    #            CARBON COMPUTATION
    # --------------------------------------------

    def get_carbon_value(
        self,
        distribution: dict["CarbonFactor", float] = None,
        **kwargs,
    ):
        """
        Return a value computed depending on the calculation method of carbon (qty/price) and the type of operation (credit/debit)
        Used in carbon.line.mixin to compute carbon debt of a line model

        Returns:
            - total_value (float): the carbon value
            - total_uncertainty_value (float): the uncertainty value
            - factor_to_details (dict): the details of the computation with this data structure:
                {
                    carbon.factor.id: {
                        carbon.factor.value.id: {
                            'value': ...,
                            'distribution': ...,
                            'uncertainty_percentage': ...,
                            'uncertainty_value': ...,
                            'compute_method': ...,
                            'carbon_value': ...,
                            'uom_id': ...,
                            'monetary_currency_id': ...,
                        },
                        carbon.factor.value.id: {
                            ...
                        },
                    },
                }

        """
        distribution = self.check_distribution(distribution)
        total_value = 0.0
        total_uncertainty_value = 0.0
        factor_to_details = {}
        for factor in self:
            value, uncertainty_value, details = factor._get_carbon_value(
                distribution.get(factor), **kwargs
            )
            total_value += value
            total_uncertainty_value += uncertainty_value
            factor_to_details[factor.id] = details

        return total_value, total_uncertainty_value, factor_to_details

    def _get_carbon_value(
        self,
        distribution: float,
        **kwargs,
    ):
        self.ensure_one()

        quantity = kwargs.get("quantity")
        from_uom_id = kwargs.get("from_uom_id")
        amount = kwargs.get("amount")
        from_currency_id = kwargs.get("from_currency_id")
        data_uncertainty_percentage = kwargs.get("data_uncertainty_percentage")

        date = kwargs.get("date", fields.Date.today())

        # --- The uncertainty percentage is common to all factor values
        uncertainty_percentage = (
            self.uncertainty_percentage**2 + data_uncertainty_percentage**2
        ) ** 0.5

        # --- These are the infos that will be returned
        result_value = 0.0
        result_details = dict()

        for factor_value in self._get_values_at_date(date):
            # Infos from factor
            (
                compute_method,
                carbon_value,
                uom_id,
                monetary_currency_id,
            ) = factor_value.get_infos()

            if compute_method == "monetary" and amount is not None and from_currency_id:
                # We convert the amount to the currency used in the factor value
                partial_value_result = carbon_value * from_currency_id._convert(
                    amount, monetary_currency_id, self.env.company, date
                )

            elif compute_method == "physical" and quantity is not None and from_uom_id:
                # Units of measure can't be converted if they are not in the same category
                if from_uom_id.category_id != uom_id.category_id:
                    raise ValidationError(
                        _(
                            "The unit of measure set for %s (%s - %s) is not in the same category as its carbon unit of measure (%s - %s)\nPlease check the carbon settings.",
                            self.name,
                            from_uom_id.name,
                            from_uom_id.category_id.name,
                            uom_id.name,
                            uom_id.category_id.name,
                        )
                    )
                partial_value_result = carbon_value * from_uom_id._compute_quantity(
                    quantity, uom_id
                )

            else:
                raise ValidationError(
                    _(
                        "To compute a carbon cost, you must pass:"
                        "\n- either a quantity and a unit of measure"
                        "\n- or a price and a currency (+ an optional date)"
                        "\n\nPassed value: "
                        "\n- Record: %s (compute method: %s)"
                        "\n- Quantity: %s, UOM: %s"
                        "\n- Amount: %s, Currency: %s",
                        self,
                        compute_method,
                        quantity,
                        from_uom_id,
                        amount,
                        from_currency_id,
                    )
                )

            # Apply the distribution and add it to the final result
            partial_value_result *= distribution
            result_value += partial_value_result

            result_details[factor_value.id] = {
                "value": partial_value_result,
                "distribution": distribution,
                "uncertainty_percentage": uncertainty_percentage,
                "uncertainty_value": partial_value_result * uncertainty_percentage,
                # Values infos are return so that if they are updated later, we still have the value at the time of the computation
                "compute_method": compute_method,
                "carbon_value": carbon_value,
                "uom_id": uom_id.id,
                "monetary_currency_id": monetary_currency_id.id,
            }

        return result_value, result_value * uncertainty_percentage, result_details

    # --------------------------------------------
    #                   ACTIONS
    # --------------------------------------------

    def _get_distribution_lines_res_ids(self, model: str) -> list[int]:
        distribution_lines = self.env["carbon.distribution.line"].search(
            [("res_model", "=", model), ("factor_id", "in", self.ids)]
        )
        return list(set(distribution_lines.mapped("res_id")))

    def action_see_child_ids(self):
        return self._generate_action(
            title=_("Child factors for"),
            model="carbon.factor",
            ids=self.child_ids.ids,
        )

    def action_see_chart_of_account_ids(self):
        return self._generate_action(
            title=_("Chart of Account for"),
            model="account.account",
            ids=self._get_distribution_lines_res_ids("account.account"),
        )

    def action_see_product_ids(self):
        return self._generate_action(
            title=_("Product for"),
            model="product.template",
            ids=self._get_distribution_lines_res_ids("product.template"),
        )

    def action_see_product_categ_ids(self):
        return self._generate_action(
            title=_("Product Category for"),
            model="product.category",
            ids=self._get_distribution_lines_res_ids("product.template"),
        )

    def action_see_account_move_ids(self):
        origins = self.env["carbon.line.origin"].search([("factor_id", "in", self.ids)])
        return self._generate_action(
            title=_("Journal Entries"), model="account.move", ids=origins.move_id.ids
        )
