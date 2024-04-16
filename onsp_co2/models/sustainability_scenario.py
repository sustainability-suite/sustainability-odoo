from odoo import fields, models


class SustainabilityScenario(models.Model):
    _name = "sustainability.scenario"
    _description = "Sustainability Scenario"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    description = fields.Text(required=True)
    end_date = fields.Date(required=True)
    active = fields.Boolean(default=True)

    action_plan_ids = fields.One2many("sustainability.action.plan", "scenario_id")
