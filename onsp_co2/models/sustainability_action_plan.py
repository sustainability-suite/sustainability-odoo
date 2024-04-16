from odoo import fields, models


class SustainabilityActionPlan(models.Model):
    _name = "sustainability.action.plan"
    _description = "Action Plan"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    description = fields.Text(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    active = fields.Boolean(default=True)

    scenario_id = fields.Many2one(
        "sustainability.scenario", required=True, ondelete="restrict"
    )

    def action_open_actions(self):
        self.ensure_one()

        action_plan = self[0]

        action = self.env.ref("onsp_co2.sustainability_action_window_action").read()[0]
        action["domain"] = [("action_plan_ids", "in", action_plan.ids)]
        return action
