from odoo import fields, models

_levels = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]


class SustainabilityAction(models.Model):
    _name = "sustainability.action"
    _description = "Sustainability Action"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    complexity = fields.Selection(_levels, required=True)
    budget = fields.Selection(_levels, required=True)
    reduction_potential = fields.Selection(_levels, required=True)
    image = fields.Image(max_width=1024, max_height=1024, required=False)

    action_plan_ids = fields.Many2one("sustainability.action.plan", required=True)
