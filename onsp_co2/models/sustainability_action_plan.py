from odoo import fields, models


class SustainabilityActionPlan(models.Model):
    _name = "sustainability.action.plan"
    _description = "Action Plan"

    name = fields.Char(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    scenario_id = fields.Many2one(
        "sustainability.scenario", required=True, ondelete="restrict"
    )
