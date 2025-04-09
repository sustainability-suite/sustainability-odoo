import logging

from odoo import api, fields, models

from odoo.addons.base.models.res_currency import Currency
from odoo.addons.uom.models.uom_uom import UoM

_logger = logging.getLogger(__name__)


class CarbonFactorValue(models.Model):
    _name = "carbon.factor.value"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Carbon Factor Value"
    _order = "date desc"

    _sql_constraints = [
        (
            "not_unique_date_type_id",
            "UNIQUE(factor_id, date, type_id)",
            "Date and Carbon Factor Type should be a unique pair",
        ),
    ]

    co2_value = fields.Float(
        tracking=True,
        string="CO2 (kg)",
        digits="Carbon Factor value",
    )
    ch4_value = fields.Float(
        tracking=True,
        string="CH4 (kgCO2e)",
        digits="Carbon Factor value",
    )
    n2o_value = fields.Float(
        tracking=True,
        string="N2O (kgCO2e)",
        digits="Carbon Factor value",
    )
    sf6_value = fields.Float(
        tracking=True,
        string="SF6 (kgCO2e)",
        digits="Carbon Factor value",
    )
    hfc_value = fields.Float(
        tracking=True,
        string="HFC (kgCO2e)",
        digits="Carbon Factor value",
    )
    pfc_value = fields.Float(
        tracking=True,
        string="PFC (kgCO2e)",
        digits="Carbon Factor value",
    )
    nf3_value = fields.Float(
        tracking=True,
        string="NF3 (kgCO2e)",
        digits="Carbon Factor value",
    )
    other_ghg_value = fields.Float(
        tracking=True,
        string="Other GHG (kgCO2e)",
        digits="Carbon Factor value",
    )

    is_ghg_detailed_value = fields.Boolean(compute="_compute_is_ghg_detailed_value")

    factor_id = fields.Many2one("carbon.factor", required=True, ondelete="cascade")
    type_id = fields.Many2one("carbon.factor.type", tracking=True)
    display_name = fields.Char(
        compute="_compute_display_name", store=True, recursive=True
    )
    carbon_currency_label = fields.Char(related="factor_id.carbon_currency_label")
    carbon_compute_method = fields.Selection(
        related="factor_id.carbon_compute_method", store=True
    )
    # Todo: check if we implement an uuid
    # uuid = fields.Char()

    date = fields.Date(required=True, tracking=True)
    comment = fields.Char()
    carbon_value = fields.Float(
        string="Total not broken down (kgCO2)",
        digits="Carbon Factor value",
        tracking=True,
        required=True,
        compute="_compute_carbon_value",
        store=True,
        readonly=False,
    )
    is_carbon_value_computed = fields.Boolean(
        default=False,
        compute="_compute_carbon_value",
        store=True,
    )

    carbon_uom_id = fields.Many2one("uom.uom", string="Unit of measure", tracking=True)
    carbon_monetary_currency_id = fields.Many2one(
        "res.currency", string="Currency", tracking=True
    )
    unit_label = fields.Char(compute="_compute_unit_label", string=" ")

    @api.depends(
        "carbon_compute_method", "carbon_monetary_currency_id", "carbon_uom_id"
    )
    def _compute_unit_label(self):
        for value in self:
            if value.carbon_compute_method == "physical" and value.carbon_uom_id:
                value.unit_label = "/ " + value.carbon_uom_id.name
            elif (
                value.carbon_compute_method == "monetary"
                and value.carbon_monetary_currency_id
            ):
                value.unit_label = "/ " + value.carbon_monetary_currency_id.name
            else:
                value.unit_label = ""

    @api.depends("factor_id.name", "type_id.name", "date", "comment")
    def _compute_display_name(self):
        for value in self:
            value.display_name = (
                f"{value.factor_id.name}"
                + (f" - {value.type_id.name}" if value.type_id else "")
                + f" ({value.date})"
            )

    def get_infos(self) -> tuple[str, float, UoM, Currency]:
        self.ensure_one()
        return (
            self.carbon_compute_method,
            self.carbon_value,
            self.carbon_uom_id,
            self.carbon_monetary_currency_id,
        )

    @api.depends(
        "co2_value",
        "ch4_value",
        "n2o_value",
        "sf6_value",
        "hfc_value",
        "pfc_value",
        "nf3_value",
        "other_ghg_value",
    )
    def _compute_carbon_value(self):
        for value in self:
            total = (
                value.co2_value
                + value.ch4_value
                + value.n2o_value
                + value.sf6_value
                + value.hfc_value
                + value.pfc_value
                + value.nf3_value
                + value.other_ghg_value
            )
            value.is_carbon_value_computed = total > 0
            if total != 0:
                value.carbon_value = total

    def action_reset_precision_value(self):
        for value in self:
            value.write(
                {
                    "co2_value": 0.0,
                    "ch4_value": 0.0,
                    "n2o_value": 0.0,
                    "sf6_value": 0.0,
                    "hfc_value": 0.0,
                    "pfc_value": 0.0,
                    "nf3_value": 0.0,
                    "other_ghg_value": 0.0,
                    "carbon_value": 0.0,
                }
            )

    def _compute_is_ghg_detailed_value(self):
        for value in self:
            value.is_ghg_detailed_value = (
                not value.is_carbon_value_computed and value.carbon_value != 0
            )
