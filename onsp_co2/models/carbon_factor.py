from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
from collections import defaultdict

import logging

_logger = logging.getLogger(__name__)

class CarbonFactor(models.Model):
    _name = "carbon.factor"
    _inherit = ["carbon.general.mixin", "mail.thread", "mail.activity.mixin"]
    _description = "Carbon Emission Factor"
    _order = "display_name"
    _parent_store = True

    ghg_view_mode = fields.Boolean(
        string="Show greenhouse gases detail", help="Toggle to show GHG details"
    )

    name = fields.Char(required=True)
    display_name = fields.Char(
        compute="_compute_display_name", store=True, recursive=True
    )
    parent_id = fields.Many2one(
        "carbon.factor", "Parent", index=True, ondelete="restrict"
    )
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many("carbon.factor", "parent_id")
    child_qty = fields.Integer(compute="_compute_child_qty")
    descendant_ids = fields.Many2many('carbon.factor', compute='_compute_descendant_ids', recursive=True)
    value_ids = fields.One2many("carbon.factor.value", "factor_id")
    
    chart_of_account_qty = fields.Integer(compute="_compute_chart_of_account_qty")
    
    product_qty = fields.Integer(compute="_compute_product_qty")
    
    product_categ_qty = fields.Integer(compute="_compute_product_categ_qty")

    carbon_compute_method = fields.Selection(
        selection=[
            ("physical", "Physical"),
            ("monetary", "Monetary"),
        ],
        string="Compute method",
    )
    carbon_currency_id = fields.Many2one('res.currency', compute="_compute_carbon_currency_id")
    carbon_currency_label = fields.Char(compute="_compute_carbon_currency_id", default="KgCo2e")
    uncertainty_value = fields.Float()

    has_invalid_value = fields.Boolean(compute="_compute_has_invalid_value")

    # related recent values
    recent_value_id = fields.Many2one(
        "carbon.factor.value", compute="_compute_recent_value", store=True
    )
    carbon_date = fields.Date(related="recent_value_id.date")
    carbon_source_id = fields.Many2one('carbon.factor.source')
    carbon_source = fields.Char(related="carbon_source_id.name", string="Source")

    carbon_value = fields.Float(related="recent_value_id.carbon_value")
    carbon_uom_id = fields.Many2one(related="recent_value_id.carbon_uom_id")
    carbon_monetary_currency_id = fields.Many2one(
        related="recent_value_id.carbon_monetary_currency_id"
    )
    unit_label = fields.Char(related="recent_value_id.unit_label")

    # --------------------------------------------

    def name_get(self) -> list[tuple[int, str]]:
        return [(factor.id, factor.display_name) for factor in self]

    @api.depends("value_ids.date")
    def _compute_recent_value(self):
        for factor in self:
            value_with_dates = factor.value_ids.filtered("date")
            factor.recent_value_id = value_with_dates and max(
                value_with_dates, key=lambda f: f.date
            )

    @api.depends("child_ids")
    def _compute_child_qty(self):
        for factor in self:
            factor.child_qty = len(factor.child_ids)

    @api.depends('child_ids.descendant_ids')
    def _compute_descendant_ids(self):
        for factor in self:
            factor.descendant_ids = factor.child_ids | factor.child_ids.descendant_ids 
    

    def _get_count_by_model(self, model: str) -> dict:
        """
        Calculate the total count of carbon factors for a given model.

        This function reads the data from the specified model, filters it based on the carbon_in_factor_id and carbon_out_factor_id,
        and then calculates the total count of carbon factors for each item in the data.

        Args:
            model (str, optional): The name of the model to calculate the carbon factors for.

        Returns:
            dict: A dictionary where the keys are the carbon_in_factor_id and the values are the total count of carbon factors for that id.
        """
        data = self.env[model].read_group(
            self._get_carbon_domain(), ["carbon_in_factor_id", "carbon_out_factor_id"], ["carbon_in_factor_id", "carbon_out_factor_id"], lazy=False
        )
        total_count = defaultdict(int)
        for item in data:
            total_count[item["carbon_in_factor_id"][0]] += item['__count']
        
        return total_count
    
    def _get_carbon_domain(self) -> list:
        """
        Generate the domain for carbon factor queries.

        This function creates a domain that can be used in queries to filter data based on the carbon_in_factor_id and carbon_out_factor_id.

        Returns:
            list: A list representing the domain for carbon factor queries. The list includes a logical OR operator and two tuples, each specifying a field name and a condition.
        """
        return ['|', ("carbon_in_factor_id", "in", self.ids), ("carbon_out_factor_id", "in", self.ids)]
    
    def _generate_action(self, model: str, title: str) -> dict:
        """
        Generate an action dictionary for the specified model and title.

        This function creates an action dictionary that can be used to open a new window in the Odoo UI. The new window will display the specified model's data, filtered by the carbon domain.

        Args:
            model (str): The name of the model to display in the new window.
            title (str): The title to display in the new window.

        Returns:
            dict: An action dictionary that can be used to open a new window in the Odoo UI.
        """
        self.ensure_one()
        return {
            "name": ("%s %s", title, self.display_name),
            "type": "ir.actions.act_window",
            "res_model": model,
            "views": [(False, "tree"), (False, "form")],
            "domain": self._get_carbon_domain(),
            "target": "current",
            "context": {
                **self.env.context,
            },
        }
               
    def _compute_chart_of_account_qty(self):
        count_data = self._get_count_by_model(model="account.account")
        for factor in self:
            factor.chart_of_account_qty = count_data.get(factor.id, 0)
                
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
                self.env.ref("onsp_co2.carbon_kilo", raise_if_not_found=False)
                or self.env["res.currency"]
            )
            factor.carbon_currency_label = factor.carbon_currency_id.currency_unit_label

    @api.depends("parent_id.display_name", "name")
    def _compute_display_name(self):
        for factor in self:
            factor.display_name = (
                f"{factor.parent_id.display_name}/{factor.name}"
                if factor.parent_id
                else factor.name
            )

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
        return super(CarbonFactor, self).write(vals)

    # --------------------------------------------
    #                 Main methods
    # --------------------------------------------

    def _get_value_at_date(self, date=None):
        self.ensure_one()
        if not self.value_ids:
            raise ValidationError(_("_get_value_at_date: No value found for the following factor (%s)" % self.name))
        if not date:
            date = fields.Date.today()
        if isinstance(date, datetime):
            date = date.date()

        values_before_date = self.value_ids.filtered(lambda v: v.date <= date)
        if values_before_date:
            return values_before_date and max(values_before_date, key=lambda v: v.date)
        else:
            return self.value_ids and min(self.value_ids, key=lambda v: v.date)

    def get_value_infos_at_date(self, date=None) -> dict:
        self.ensure_one()
        value_id = self._get_value_at_date(date)
        return value_id.get_infos_dict()

    # --------------------------------------------
    #                   ACTIONS
    # --------------------------------------------

    def action_see_child_ids(self):
        return self._generate_action(title=_("Child factors for"), model="carbon.factor")
        
    def action_see_chart_of_account_ids(self):
        return self._generate_action(title=_("Chart of Account for"), model="account.account")

    def action_see_product_ids(self):
        return self._generate_action(title=_("Product for"), model="product.template")
        
    def action_see_product_categ_ids(self):
        return self._generate_action(title=_("Product Category for"), model="product.category")
