from odoo import fields, models


class Approach(models.Model):
    _name = "sustainability.approach"
    _description = "Approach"

    name = fields.Char(
        required=True,
        help="Examples: Physical control, Operational control, Share of capital",
    )


class ApproachCharacterization(models.Model):
    _name = "sustainability.approach.characterization"
    _description = "Approach Characterization"

    name = fields.Char(
        required=True,
        help="Examples: Operated, Non-operated, Supported, Non-operated, Unsupported",
    )
    approach_id = fields.Many2one(comodel_name="sustainability.approach", required=True)
    regulatory_nomenclature_category_id = fields.Many2one(
        comodel_name="sustainability.nomenclature.category", required=True
    )
    is_default = fields.Boolean(
        default=False,
        help='Allows defining a default characterization for the chosen approach for the default nomenclature. For example, for "Energy" -> "Non-operated"',
    )
