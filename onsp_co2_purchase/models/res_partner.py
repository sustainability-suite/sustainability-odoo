from odoo import models

class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "carbon.mixin"]

    def _get_carbon_value_fallback_records(self) -> list:
        self.ensure_one()
        res = super(ResPartner, self)._get_carbon_value_fallback_records()
        return res + [self.parent_id]

    def _get_carbon_sale_value_fallback_records(self) -> list:
        self.ensure_one()
        res = super(ResPartner, self)._get_carbon_sale_value_fallback_records()
        return res + [self.parent_id]
