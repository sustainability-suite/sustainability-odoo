from odoo import models, fields
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)


WEEKS_PER_MONTH = 4


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    carbon_commuting_ids = fields.One2many('carbon.hr.commuting', 'employee_id', string="Employee commuting records")
   
    def _get_carbon_commuting_line_vals(self) -> dict:
        self.ensure_one()
        value, details = self._compute_commuting_carbon()
        return {
            'carbon_debt': value,
            'name': f'{self.name}{details}',
            'account_id': self.company_id.employee_commuting_account_id.id,
            'debit': 0,
            'credit': 0,
            'carbon_is_locked': True,
            'partner_id': self.address_home_id.id,
        }

    def _compute_commuting_carbon(self):
        self.ensure_one()
        commuting_details = ""
        # Extra check, maybe you don't need it
        if not self.carbon_commuting_ids:
            commuting_details = f'No commuting for {self.name}'

        total_commuting_value = 0
        # Calculate carbon emissions based on employee's commuting records
        for commuting in self.carbon_commuting_ids:
            # I removed the if statement, you can add it back if it's necessary
            total_commuting_value += commuting.carbon_value
            commuting_details += f"\n| {commuting.carbon_factor_id.name} : {commuting.distance_km} Km "

        # Convert weekly to monthly
        # 4 weeks / months for a ratio of 48 weeks / year (5 weeks holiday)
        total_commuting_value *= WEEKS_PER_MONTH
        return total_commuting_value, commuting_details
