from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class CarbonFactorValue(models.Model):
    _name = "carbon.factor.value"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "carbon.factor.value"
    _order = "date desc"

    _sql_constraints = [
        ('not_negative_carbon_value', 'CHECK(carbon_value >= 0)', 'CO2e value can not be negative !'),
    ]

    factor_id = fields.Many2one('carbon.factor', required=True, ondelete='cascade')
    display_name = fields.Char(compute="_compute_display_name", store=True, recursive=True)
    carbon_currency_label = fields.Char(related="factor_id.carbon_currency_label")
    carbon_compute_method = fields.Selection(related="factor_id.carbon_compute_method", store=True)
    # Todo: check if we implement an uuid
    # uuid = fields.Char()

    # Todo: check if we use a m2o (i.e. res.partner)
    date = fields.Date(required=True)
    source = fields.Char()
    carbon_value = fields.Float(
        string="CO2e value",
        digits="Carbon value",
        tracking=True,
        required=True
    )
    carbon_uom_id = fields.Many2one("uom.uom", string="Unit of measure")
    carbon_monetary_currency_id = fields.Many2one("res.currency", string="Currency")
    unit_label = fields.Char(compute="_compute_unit_label", string=" ")

    @api.depends('carbon_compute_method', 'carbon_monetary_currency_id', 'carbon_uom_id')
    def _compute_unit_label(self):
        for value in self:
            if value.carbon_compute_method == 'physical' and value.carbon_uom_id:
                value.unit_label = "/ " + value.carbon_uom_id.name
            elif value.carbon_compute_method == 'monetary' and value.carbon_monetary_currency_id:
                value.unit_label = "/ " + value.carbon_monetary_currency_id.name
            else:
                value.unit_label = ""


    @api.depends('factor_id.name', 'date', 'source')
    def _compute_display_name(self):
        for value in self:
            value.display_name = f"{value.factor_id.name} - {value.date}" + (f" ({value.source})" if value.source else "")


    def get_infos_dict(self):
        self.ensure_one()
        return {
            'compute_method': self.carbon_compute_method,
            'carbon_value': self.carbon_value,
            'carbon_uom_id': self.carbon_uom_id,
            'carbon_monetary_currency_id': self.carbon_monetary_currency_id,
            'carbon_value_origin': self.display_name,
        }
