import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CarbonDistributionLine(models.Model):
    _name = "carbon.distribution.line"
    _description = "Carbon Distribution Line"

    _sql_constraints = [
        (
            "positive_percentage",
            "CHECK(percentage > 0)",
            "Percentage must be higher than zero",
        ),
        (
            "max_limit_percentage",
            "CHECK(percentage <= 1)",
            "Percentage cannot be higher than 100%",
        ),
    ]

    # Fake Many2one that is used in the One2many field in `carbon.mixin`
    res_model_id = fields.Many2one(
        "ir.model", index=True, ondelete="cascade", required=True
    )
    res_model = fields.Char(
        related="res_model_id.model",
        index=True,
        precompute=True,
        store=True,
        readonly=True,
    )
    res_id = fields.Many2oneReference(index=True, model_field="res_model")
    res_in_id = fields.Many2oneReference(
        index=True,
        model_field="res_model",
        compute="_compute_res_in_out_id",
        inverse="_inverse_res_in_out_id",
        store=True,
    )
    res_out_id = fields.Many2oneReference(
        index=True,
        model_field="res_model",
        compute="_compute_res_in_out_id",
        inverse="_inverse_res_in_out_id",
        store=True,
    )

    factor_id = fields.Many2one(
        comodel_name="carbon.factor",
        string="Carbon Factor",
        required=True,
        domain="[('recent_value_id', '!=', False)]",
    )
    percentage = fields.Float(required=True)
    carbon_type = fields.Selection(
        [
            ("in", "In"),
            ("out", "Out"),
            ("template", "Template"),
        ],
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "res_model" in vals:
                vals["res_model_id"] = self.env["ir.model"]._get(vals["res_model"]).id
        res = super().create(vals_list)
        return res

    def get_record(self):
        self.ensure_one()
        return self.env[self.res_model].browse(self.res_id).exists()

    @api.depends("res_id", "carbon_type")
    def _compute_res_in_out_id(self):
        for distribution in self:
            if distribution.carbon_type == "in":
                distribution.res_in_id = distribution.res_id
                distribution.res_out_id = False
            elif distribution.carbon_type == "out":
                distribution.res_out_id = distribution.res_id
                distribution.res_in_id = False
            elif distribution.carbon_type == "template":
                distribution.res_in_id = distribution.res_out_id = False

    def _inverse_res_in_out_id(self):
        for distribution in self:
            if distribution.carbon_type == "in":
                distribution.res_id = distribution.res_in_id
                distribution.res_out_id = False
            elif distribution.carbon_type == "out":
                distribution.res_id = distribution.res_out_id
                distribution.res_in_id = False
