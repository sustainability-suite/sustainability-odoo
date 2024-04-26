from odoo import _, fields, models

_levels = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]


class SustainabilityAction(models.Model):
    _name = "sustainability.action"
    _description = "Sustainability Action"
    _inherit = ["mail.thread", "mail.activity.mixin", "common.mixin"]

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(required=True, tracking=True)
    complexity = fields.Selection(_levels, required=True, tracking=True)
    budget = fields.Selection(_levels, required=True, tracking=True)
    reduction_potential = fields.Selection(_levels, required=True, tracking=True)
    image = fields.Image(max_width=1920, max_height=1920, required=False)
    active = fields.Boolean(default=True)

    action_plan_ids = fields.Many2many("sustainability.action.plan", required=False)
    action_plan_qty = fields.Integer(compute="_compute_action_plan_qty")
    scenario_qty = fields.Integer(compute="_compute_scenario_qty")

    def _compute_action_plan_qty(self):
        for action in self:
            action.action_plan_qty = len(action.action_plan_ids)

    def _compute_scenario_qty(self):
        for action in self:
            action.scenario_qty = len(self.action_plan_ids.scenario_id.ids)

    def action_see_action_plans(self):
        return self._generate_action(
            title=_("Action Plans for"),
            model="sustainability.action.plan",
            ids=self.action_plan_ids.ids,
        )

    def action_see_scenarios(self):
        return self._generate_action(
            title=_("Scenario for"),
            model="sustainability.scenario",
            ids=self.action_plan_ids.scenario_id.ids,
        )
