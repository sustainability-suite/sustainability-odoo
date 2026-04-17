from datetime import datetime

from odoo import api, fields, models

from odoo.addons.hr_homeworking.models.hr_homeworking import DAYS

WEEKS_PER_MONTH = 4
# 4 weeks / months for a ratio of 48 weeks / year (5 weeks holiday)
# is going to be computed later


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    carbon_commuting_ids = fields.One2many(
        "carbon.hr.commuting", "employee_id", string="Employee commuting records"
    )

    work_days_home = fields.Integer(
        string="Work Days at Home",
        compute="_compute_work_days_home",
        store=True,
        help="Number of days per week the employee works from home.",
    )
    has_location = fields.Boolean(
        default=False,
        store=True,
    )

    @api.depends(
        *DAYS,
        "exceptional_location_id",
    )
    def _compute_work_days_home(self):
        for employee in self:
            home_days = 0

            for day in DAYS:
                location = employee[day] or employee.exceptional_location_id

                if location and location.location_type == "home":
                    home_days += 1
                if location and location.location_type:
                    employee.has_location = True

            employee.work_days_home = home_days

    def _get_carbon_commuting_line_vals(self, date) -> dict:
        self.ensure_one()
        if not date:
            date = datetime.now()
        (
            value,
            commuting_details,
            uncertainty_value,
            carbon_details,
        ) = self._calculate_commuting_carbon(date)
        return {
            "carbon_debt": value,
            "carbon_uncertainty_value": uncertainty_value,
            "carbon_data_uncertainty_percentage": uncertainty_value / (value or 1),
            "name": f"{self.name}{commuting_details}",
            "account_id": self.company_id.employee_commuting_account_id.id,
            "debit": 0,
            "credit": 0,
            "carbon_is_locked": True,
            # TODO: discuss partner logic with BCH
            "partner_id": self.user_partner_id.id or self.address_id.id or False,
            "carbon_origin_json": {"mode": "auto", "details": carbon_details},
        }

    def _calculate_commuting_carbon(self, date):
        self.ensure_one()
        total_commuting_details = ""
        total_carbon_details = dict()
        # Extra check, maybe you don't need it
        if not self.carbon_commuting_ids:
            total_commuting_details = f"No commuting for {self.name}"

        total_commuting_value = 0
        total_uncertainty_value = 0
        # Calculate carbon emissions based on employee's commuting records
        for commuting in self.carbon_commuting_ids:
            # I removed the if statement, you can add it back if it's necessary
            (
                commuting_value,
                uncertainty_value,
                carbon_details,
            ) = commuting.get_commuting_carbon_value_at_date(date)
            total_commuting_value += commuting_value
            total_uncertainty_value += uncertainty_value
            total_commuting_details += f"\n| {commuting.carbon_factor_id.name} : {commuting.distance_km * WEEKS_PER_MONTH} Km"
            total_carbon_details |= carbon_details
        return (
            total_commuting_value,
            total_commuting_details,
            total_uncertainty_value,
            total_carbon_details,
        )
