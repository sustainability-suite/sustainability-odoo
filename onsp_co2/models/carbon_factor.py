from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


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
    value_ids = fields.One2many("carbon.factor.value", "factor_id")

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
    carbon_source = fields.Char(related="carbon_source_id.name")

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
        self.ensure_one()
        return {
            "name": _("Child factors for %s", self.display_name),
            "type": "ir.actions.act_window",
            "res_model": "carbon.factor",
            "views": [(False, "tree"), (False, "form")],
            "domain": [("parent_id", "=", self.id)],
            "target": "current",
            "context": {
                **self.env.context,
            },
        }
