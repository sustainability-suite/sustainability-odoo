
from odoo import models, fields, api



class CarbonCommuting(models.Model):
    _name = "carbon.hr.commuting"


    carbon_factor_id = fields.Many2one('carbon.factor', domain="[('id', 'in', allowed_carbon_factor_ids),('carbon_value', '!=', False)]", string="Transport mean")
    allowed_carbon_factor_ids = fields.Many2many('carbon.factor', related="employee_id.company_id.employee_commuting_carbon_factor_id.descendant_ids", domain=lambda self: [('carbon_uom_id', '=', self.env.ref('uom.product_uom_km').id)])
    distance_km = fields.Integer(string="Average weekly distance in kilometers")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    carbon_value = fields.Float(compute="_compute_carbon_value", digits="Carbon value")

    
    @api.depends('carbon_factor_id.carbon_value', 'distance_km')
    def _compute_carbon_value(self):
        for commuting in self:
            commuting.carbon_value = commuting.carbon_factor_id.carbon_value * commuting.distance_km
