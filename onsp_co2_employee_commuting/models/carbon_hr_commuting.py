
from odoo import models, fields, api
from .hr_employee import WEEKS_PER_MONTH



class CarbonCommuting(models.Model):
    _name = "carbon.hr.commuting"


    carbon_factor_id = fields.Many2one('carbon.factor', domain="[('id', 'in', allowed_carbon_factor_ids),('carbon_value', '!=', False)]", string="Transport mean", required=True)
    allowed_carbon_factor_ids = fields.Many2many('carbon.factor', related="employee_id.company_id.employee_commuting_carbon_factor_id.descendant_ids", domain=lambda self: [('carbon_uom_id', '=', self.env.ref('uom.product_uom_km').id)])
    distance_km = fields.Integer(string="Average weekly distance in kilometers")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    
    def get_commuting_carbon_value_at_date(self, date):
        self.ensure_one()
        commuting_value, commmuting_uncertainty_value, infos = self.carbon_factor_id.get_carbon_value(
            date=date, carbon_type='in', quantity=self.distance_km * WEEKS_PER_MONTH, 
            from_uom_id=self.env.ref('uom.product_uom_km'), data_uncertainty_percentage=0)
        return commuting_value, commmuting_uncertainty_value
    
