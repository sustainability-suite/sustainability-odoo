from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .hr_employee import WEEKS_PER_MONTH


class CarbonCommuting(models.Model):
    _name = "carbon.hr.commuting"
    _description = "Carbon Employee Commuting"
    _order = "end_date desc"

    carbon_factor_id = fields.Many2one(
        "carbon.factor",
        domain="[('id', 'in', allowed_carbon_factor_ids),('carbon_value', '!=', False)]",
        string="Transport mean",
        required=True,
    )
    allowed_carbon_factor_ids = fields.Many2many(
        "carbon.factor",
        related="employee_id.company_id.employee_commuting_carbon_factor_id.descendant_ids",
        domain=lambda self: [
            ("carbon_uom_id", "=", self.env.ref("uom.product_uom_km").id)
        ],
    )
    distance_km = fields.Integer(string="Average weekly distance in kilometers")
    employee_id = fields.Many2one("hr.employee", string="Employee")

    start_date = fields.Date(string="From", required=True, default=fields.Date.today)
    end_date = fields.Date(string="To")

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        if self.filtered(lambda r: r.end_date and r.end_date < r.start_date):
           raise ValidationError("End date must be later than or equal to start date.")

    def get_commuting_carbon_value_at_date(self, date):
        self.ensure_one()
        (
            commuting_value,
            commmuting_uncertainty_value,
            details,
        ) = self.carbon_factor_id.get_carbon_value(
            date=date,
            carbon_type="in",
            quantity=self.distance_km * WEEKS_PER_MONTH,
            from_uom_id=self.env.ref("uom.product_uom_km"),
            data_uncertainty_percentage=0,
        )
        return commuting_value, commmuting_uncertainty_value, details
