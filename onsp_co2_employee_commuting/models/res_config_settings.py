from odoo import fields, models, api
from datetime import datetime


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    employee_commuting_carbon_factor_id = fields.Many2one('carbon.factor', related='company_id.employee_commuting_carbon_factor_id', readonly=False)
    employee_commuting_journal_id = fields.Many2one('account.journal', related='company_id.employee_commuting_journal_id', readonly=False)
    employee_commuting_account_id = fields.Many2one('account.account', related='company_id.employee_commuting_account_id', readonly=False)
    employee_commuting_carbon_cronjob_active = fields.Boolean('Cron job active', related='company_id.employee_commuting_carbon_cronjob_active', readonly=False)

    def set_values(self):
        super().set_values()
        employee_commuting_carbon_cron = self.env.ref('onsp_co2_employee_commuting.cron_carbon_employee_commuting_account_move_create').sudo()
        if employee_commuting_carbon_cron and employee_commuting_carbon_cron.active != self.employee_commuting_carbon_cronjob_active:
            employee_commuting_carbon_cron.active = self.employee_commuting_carbon_cronjob_active
