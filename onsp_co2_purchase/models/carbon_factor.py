from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class CarbonFactor(models.Model):
    _inherit = "carbon.factor"
    
    contact_qty = fields.Integer(compute="_compute_contact_qty")
    
    # --------------------------------------------
           
    def _compute_contact_qty(self):
        count_data = self._get_count_by_model(model="res.partner")
        for factor in self:
            factor.contact_qty = count_data.get(factor.id, 0)
            
    # --------------------------------------------
    #                   ACTIONS
    # --------------------------------------------
            
    def action_see_contact_ids(self):
        return self._generate_action(title="Contact", model="res.partner")
        
