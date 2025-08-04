import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CarbonDistributionTemplate(models.Model):
    _name = "carbon.distribution.template"
    _description = "Carbon Distribution Template"

    name = fields.Char(required=True)
    carbon_distribution_line_ids = fields.One2many(
        "carbon.distribution.line",
        "res_id",
        "Distribution lines",
        auto_join=True,
        domain="[('carbon_type', '=', 'template')]",
        required=True,
    )
    carbon_has_valid_distribution = fields.Boolean(
        compute="_compute_carbon_has_valid_distribution"
    )

    @api.constrains("carbon_distribution_line_ids")
    def _check_carbon_distribution(self):
        for record in self:
            if not record.has_valid_carbon_distribution():
                raise ValidationError(
                    _(
                        "The total percentage of distribution lines must be equal to 100% (for template)"
                    )
                )

    @api.depends("carbon_distribution_line_ids.percentage")
    def _compute_carbon_has_valid_distribution(self):
        for template in self:
            template.carbon_has_valid_distribution = (
                template.has_valid_carbon_distribution()
            )

    def has_valid_carbon_distribution(self):
        if not self:
            return False
        self.ensure_one()
        total_percentage = sum(
            [line.percentage for line in self.carbon_distribution_line_ids]
        )
        return total_percentage == 1
