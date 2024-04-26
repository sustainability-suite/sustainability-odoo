from odoo import _, fields, models


class SustainabilityScenario(models.Model):
    _name = "sustainability.scenario"
    _description = "Sustainability Scenario"
    _inherit = ["mail.thread", "mail.activity.mixin", "common.mixin"]

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(required=True, tracking=True)
    end_date = fields.Date(required=True, tracking=True)
    active = fields.Boolean(default=True)

    action_plan_ids = fields.One2many("sustainability.action.plan", "scenario_id")
    action_plan_qty = fields.Integer(compute="_compute_action_plan_qty")
    action_qty = fields.Integer(compute="_compute_action_qty")

    def _compute_action_plan_qty(self):
        for scenario in self:
            scenario.action_plan_qty = len(scenario.action_plan_ids)

    def _compute_action_qty(self):
        for scenario in self:
            actions = self.env["sustainability.action"].search(
                [("action_plan_ids.scenario_id", "=", scenario.id)]
            )
            scenario.action_qty = len(actions)

    def action_see_action_plans(self):
        return self._generate_action(
            title=_("Action Plans for"),
            model="sustainability.action.plan",
            ids=self.action_plan_ids.ids,
        )

    def action_see_actions(self):
        return self._generate_action(
            title=_("Actions for"),
            model="sustainability.action",
            ids=self.action_plan_ids.action_ids.ids,
        )
