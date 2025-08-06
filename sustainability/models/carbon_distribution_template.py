import logging
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CarbonDistributionTemplate(models.Model):
    _name = "carbon.distribution.template"
    _description = "Carbon Distribution Template"
    _inherit = ["carbon.common.mixin"]

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

    product_template_qty = fields.Integer(compute="_compute_product_template_qty")
    product_product_qty = fields.Integer(compute="_compute_product_product_qty")

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

    def _compute_product_template_qty(self):
        count_data = self._get_count_by_model(model="product.template")
        for template in self:
            template.product_template_qty = count_data.get(template.id, 0)

    def _compute_product_product_qty(self):
        count_data = self._get_count_by_model(model="product.product")
        for template in self:
            template.product_product_qty = count_data.get(template.id, 0)

    def action_see_product_template_ids(self):
        return self._generate_action(
            title=_("Product Templates for"),
            model="product.template",
            ids=self._get_distribution_template_res_ids("product.template"),
        )

    def action_see_product_product_ids(self):
        return self._generate_action(
            title=_("Product Variants for"),
            model="product.product",
            ids=self._get_distribution_template_res_ids("product.product"),
        )

    def _get_distribution_template_res_ids(self, model: str) -> list[int]:
        # fmt: off
        domain = [
            "|",
                "&",
                "&",
                    ("carbon_in_is_manual", "=", True),
                    ("carbon_in_use_distribution", "=", True),
                    ("carbon_in_distribution_template_id", "in", self.ids),
                "&",
                "&",
                    ("carbon_out_is_manual", "=", True),
                    ("carbon_out_use_distribution", "=", True),
                    ("carbon_out_distribution_template_id", "in", self.ids),
        ]
        # fmt: on
        return self.env[model].search(domain).ids

    def _get_count_by_model(self, model: str) -> dict:
        total_count = defaultdict(int)
        records = self.env[model].browse(self._get_distribution_template_res_ids(model))
        for record in records:
            record_templates_ids = set()  # to avoid adding 2 for the same record (e.g. in and out have the same value)
            for carbon_type in ("in", "out"):
                if template := record[f"carbon_{carbon_type}_distribution_template_id"]:
                    record_templates_ids.add(template.id)
            for template_id in record_templates_ids:
                total_count[template_id] += 1

        return total_count
