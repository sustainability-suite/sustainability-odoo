from odoo import fields, models


class Scenario(models.Model):
    _name = "scenario"
    _description = "Scenario"

    name = fields.Char(required=True)
    end_date = fields.Date(required=True)
