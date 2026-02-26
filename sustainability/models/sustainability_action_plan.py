from odoo import _, fields, models


class SustainabilityActionPlan(models.Model):
    _name = "sustainability.action.plan"
    _description = "Sustainability Action Plan"
    _inherit = ["mail.thread", "mail.activity.mixin", "carbon.common.mixin"]

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(required=True, tracking=True)
    start_date = fields.Date(required=True, tracking=True)
    end_date = fields.Date(required=True, tracking=True)
    active = fields.Boolean(default=True)

    scenario_id = fields.Many2one(
        "sustainability.scenario", required=True, ondelete="restrict", tracking=True
    )
    action_ids = fields.Many2many("sustainability.action", string="Actions")

    action_qty = fields.Integer(compute="_compute_action_qty")

    def _compute_action_qty(self):
        for action in self:
            action.action_qty = len(action.action_ids)

    def action_see_actions(self):
        return self._generate_action(
            title=_("Actions for"),
            model="sustainability.action",
            ids=self.action_ids.ids,
        )
