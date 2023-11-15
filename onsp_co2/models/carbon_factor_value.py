from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class CarbonFactorValue(models.Model):
    _name = "carbon.factor.value"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "carbon.factor.value"
    _order = "date desc"

    _sql_constraints = [
        (
            "not_negative_carbon_value",
            "CHECK(carbon_value >= 0)",
            "CO2e value can not be negative !",
        ),
        (
            "not_negative_co2_value",
            "CHECK(co2_value >= 0)",
            "CO2e value can not be negative !",
        ),
        (
            "not_negative_ch4_value",
            "CHECK(ch4_value >= 0)",
            "CH4 value can not be negative !",
        ),
        (
            "not_negative_n2o_value",
            "CHECK(n2o_value >= 0)",
            "N2O value can not be negative !",
        ),
        (
            "not_negative_sf6_value",
            "CHECK(sf6_value >= 0)",
            "SF6 value can not be negative !",
        ),
        (
            "not_negative_hfc_value",
            "CHECK(hfc_value >= 0)",
            "HFC value can not be negative !",
        ),
        (
            "not_negative_pfc_value",
            "CHECK(pfc_value >= 0)",
            "PFC value can not be negative !",
        ),
        (
            "not_negative_other_ghg_value",
            "CHECK(other_ghg_value >= 0)",
            "Other GHG value can not be negative !",
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
    other_ghg_value = fields.Float(
        tracking=True,
        string="Other GHG (kgCO2e)",
        digits="Carbon Factor value",
    )

    is_ghg_detailed_value = fields.Boolean(compute="_compute_is_ghg_detailed_value")

    factor_id = fields.Many2one("carbon.factor", required=True, ondelete="cascade")
    display_name = fields.Char(
        compute="_compute_display_name", store=True, recursive=True
    )
    carbon_currency_label = fields.Char(related="factor_id.carbon_currency_label")
    carbon_compute_method = fields.Selection(
        related="factor_id.carbon_compute_method", store=True
    )
    # Todo: check if we implement an uuid
    # uuid = fields.Char()

    # Todo: check if we use a m2o (i.e. res.partner)
    date = fields.Date(required=True)
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
        compute_sudo=True,
    )

    carbon_uom_id = fields.Many2one("uom.uom", string="Unit of measure")
    carbon_monetary_currency_id = fields.Many2one("res.currency", string="Currency")
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

    @api.depends("factor_id.name", "date", "comment")
    def _compute_display_name(self):
        for value in self:
            value.display_name = f"{value.factor_id.name} - {value.date}" + (
                f" ({value.comment})" if value.comment else ""
            )

    def get_infos_dict(self):
        self.ensure_one()
        return {
            "compute_method": self.carbon_compute_method,
            "carbon_value": self.carbon_value,
            "carbon_uom_id": self.carbon_uom_id,
            "carbon_monetary_currency_id": self.carbon_monetary_currency_id,
            "carbon_value_origin": self.display_name,
        }

    @api.depends(
        "co2_value",
        "ch4_value",
        "n2o_value",
        "sf6_value",
        "hfc_value",
        "pfc_value",
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
                    "other_ghg_value": 0.0,
                    "carbon_value": 0.0,
                }
            )

    def _compute_is_ghg_detailed_value(self):
        for value in self:
            value.is_ghg_detailed_value = (
                not value.is_carbon_value_computed and value.carbon_value != 0
            )
