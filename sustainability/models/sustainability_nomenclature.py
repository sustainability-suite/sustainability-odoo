from odoo import fields, models


class Nomenclature(models.Model):
    _name = "sustainability.nomenclature"
    _description = "Sustainability Nomenclature"

    name = fields.Char(
        required=True,
        help="Examples: Carbon Balance, GHG Protocol, ISO/TR 14069, Regulatory Method",
    )
    url = fields.Char(required=True)
    is_default = fields.Boolean(
        default=False,
        help="To manage categories of the regulatory method (Energy, Non-Energy, Inputs...) guiding the characterizations (Physical control, Operational control...)",
    )


class NomenclatureCategory(models.Model):
    _name = "sustainability.nomenclature.category"
    _description = "Nomenclature Category"

    name = fields.Char(
        required=True,
        help="Examples: Direct GHG emissions, Indirect emissions associated with energy",
    )
    description = fields.Char(required=True)
    reporting_section = fields.Char(required=True)
    nomenclature_id = fields.Many2one(
        comodel_name="sustainability.nomenclature", required=True
    )


class NomenclatureSubCategory(models.Model):
    _name = "sustainability.nomenclature.sub_category"
    _description = "Nomenclature Sub Category"

    _inherit = ["mail.thread", "mail.activity.mixin", "carbon.common.mixin"]

    name = fields.Char(
        required=True,
        help="Examples: Direct emissions from fixed combustion sources, Upstream freight transport",
    )
    description = fields.Char(required=True)
    reporting_section = fields.Char(required=True)
    category_id = fields.Many2one(
        comodel_name="sustainability.nomenclature.category", required=True
    )
    emission_sources = fields.Char()
    activity_data = fields.Char()
    other_information = fields.Char()
    examples = fields.Char()


class NomenclatureReporting(models.Model):
    _name = "sustainability.nomenclature.reporting"
    _description = "Nomenclature Reporting"

    nomenclature_sub_category_id = fields.Many2one(
        comodel_name="sustainability.nomenclature.sub_category", required=True
    )
    emission_factor_type_id = fields.Many2one(comodel_name="carbon.factor.type")
    approach_characterization_id = fields.Many2one(
        comodel_name="sustainability.approach.characterization",
    )
    emission_factor_category_id = fields.Many2one(comodel_name="carbon.factor")
    rule_order = fields.Integer(required=True, help="Move items up/down")
