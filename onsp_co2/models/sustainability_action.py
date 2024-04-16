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

    name = fields.Char(required=True)
    description = fields.Text(required=True)
    complexity = fields.Selection(_levels, required=True)
    budget = fields.Selection(_levels, required=True)
    reduction_potential = fields.Selection(_levels, required=True)
    image_1920 = fields.Image(max_width=1920, max_height=1920, required=False)
    image_512 = fields.Image(
        related="image_1920", max_width=512, max_height=512, read_only=True
    )
    image_128 = fields.Image(
        related="image_1920", max_width=128, max_height=128, read_only=True
    )
    active = fields.Boolean(default=True)

    action_plan_ids = fields.Many2many("sustainability.action.plan", required=False)
