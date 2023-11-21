from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    is_employee_commuting_carbon = fields.Boolean("Employees' commuting carbon emissions", default=False)
    employee_commuting_carbon_date = fields.Date('Employee commuting date')
