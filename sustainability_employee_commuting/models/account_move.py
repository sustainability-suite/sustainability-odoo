from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_employee_commuting_carbon = fields.Boolean(
        "Employees' commuting carbon emissions", default=False, copy=False
    )
    employee_commuting_carbon_date = fields.Date(
        "Employee commuting date", default=False, copy=False
    )

    def _sustainability_empty_carbon_fields(self):
        self.is_employee_commuting_carbon = self.employee_commuting_carbon_date = False
