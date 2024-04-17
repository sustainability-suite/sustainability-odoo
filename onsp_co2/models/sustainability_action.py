from odoo import fields, models

_levels = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]


class SustainabilityAction(models.Model):
    _name = "sustainability.action"
    _description = "Sustainability Action"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(required=True, tracking=True)
    complexity = fields.Selection(_levels, required=True, tracking=True)
    budget = fields.Selection(_levels, required=True, tracking=True)
    reduction_potential = fields.Selection(_levels, required=True, tracking=True)
    image = fields.Image(max_width=1920, max_height=1920, required=False)
    active = fields.Boolean(default=True)

    action_plan_ids = fields.Many2many("sustainability.action.plan", required=False)
