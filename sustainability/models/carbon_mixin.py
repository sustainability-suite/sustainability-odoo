from typing import Any

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .carbon_factor import CarbonFactor

# DO NOT DELETE
# def auto_depends(cls):
#     all_fb_rec = getattr(cls, '_fallback_records', list()) + getattr(CarbonMixin, '_fallback_records', list())
#     all_fb_rec_fields = getattr(cls, '_fallback_records_fields', list()) + getattr(CarbonMixin, '_fallback_records_fields', list())
#
#     for prefix in ['carbon_in', 'carbon_out']:
#         fb_rec_fields = [f"{prefix}_{f}" for f in all_fb_rec_fields]
#         res = [f"{fr}.{f}" for fr in all_fb_rec for f in fb_rec_fields]
#         setattr(cls, f'_compute_{prefix}_value', api.depends(*res)(getattr(cls, f'_compute_{prefix}_value', getattr(CarbonMixin, f'_compute_{prefix}_value'))))
#
#     # cls._compute_carbon_out_value = api.depends(*res)(getattr(cls, '_compute_carbon_out_value', getattr(CarbonMixin, '_compute_carbon_out_value')))
#     return cls


# DO NOT DELETE
# def auto_carbon_compute(cls):
#     try:
#         carbon_mixin_class = CarbonMixin
#
#         def __init__(self, env, ids, prefetch_ids):
#             super(cls, self).__init__(env, ids, prefetch_ids)
#             if hasattr(cls, '_fallback_records'):
#                 # Need to copy the method to add
#                 cls._compute_carbon_in_mode = _auto_depends(carbon_mixin_class, cls, 'carbon_in')
#                 cls._compute_carbon_out_mode = _auto_depends(carbon_mixin_class, cls, 'carbon_out')
#
#         cls.__init__ = __init__
#     except:
#         pass
#     return cls


# Todo: make this extendable from sub modules


class CarbonMixin(models.AbstractModel):
    _name = "carbon.mixin"
    _description = "A mixin used to add carbon values on any model"
    _carbon_types = ["in", "out"]
    _fallback_records = []

    # TODO: Thinks about compute this from env['carbon.line.mixin']._get_computation_levels_mapping()
    @api.model
    def _CARBON_MODELS(cls):
        return [
            "carbon.factor",
            "product.category",
            "product.product",
            "product.supplierinfo",
            "product.template",
            "res.partner",
            "res.company",
            "res.country",
        ]

    @api.constrains("carbon_in_use_distribution", "carbon_in_distribution_line_ids")
    def _check_carbon_in_distribution(self):
        for record in self.filtered("carbon_in_use_distribution"):
            if not record.has_valid_carbon_distribution("in"):
                raise ValidationError(
                    _(
                        "The total percentage of distribution lines must be equal to 100% (for carbon `in`)"
                    )
                )

    @api.model
    def _get_available_carbon_compute_methods(self) -> list[tuple[str, str]]:
        return [
            ("physical", "Physical"),
            ("monetary", "Monetary"),
        ]

    @api.model
    def _selection_fallback_model(self):
        return [
            (x, _(self.env[x]._description))
            for x in self._CARBON_MODELS()
            if x in self.env
        ]

    def get_allowed_factors(self):
        return self.env["carbon.factor"].search(self._get_allowed_factors_domain())

    def _get_allowed_factors_domain(self):
        """Used for distribution lines mainly, to override on specific models"""
        return [
            (
                "carbon_compute_method",
                "in",
                [method[0] for method in self._get_available_carbon_compute_methods()],
            ),
            ("recent_value_id", "!=", False),
        ]

    def _get_uom_filtered_factors_domain(self, uom_id):
        """Filter physical EF on product uom & weight + include monetary ones."""

        weight_uom_category = self.env.ref("uom.product_uom_categ_kgm")
        return [
            "|",
            ("carbon_compute_method", "=", "monetary"),
            "&",
            ("carbon_compute_method", "=", "physical"),
            "|",
            ("carbon_uom_id", "=", uom_id),
            ("carbon_uom_id.category_id", "=", weight_uom_category.id),
        ]

    # --------------------------------------------
    #               SHARED INFOS
    # --------------------------------------------
    carbon_allowed_factor_ids = fields.Many2many(
        "carbon.factor", compute="_compute_carbon_allowed_factor_ids"
    )
    model_name = fields.Char(
        compute="_compute_model_name"
    )  # Used in view, passed in context for distribution lines

    # --------------------------------------------
    #           General/Purchase value
    # --------------------------------------------
    carbon_in_is_manual = fields.Boolean(default=False)
    carbon_in_mode = fields.Selection(
        selection=[
            ("auto", "Automatic"),
            ("manual", "Manual"),
        ],
        default="auto",
        compute="_compute_carbon_in_mode",
        store=True,
    )  # TODO: rename selection list with a migration script for XML consistency (once tha values are finalized)
    carbon_in_factor_id = fields.Many2one(
        "carbon.factor",
        string="Emission Factor Purchases",
        ondelete="set null",
        domain="[('id', 'in', carbon_allowed_factor_ids)]",
    )
    carbon_in_fallback_reference = fields.Reference(
        selection="_selection_fallback_model", readonly=True, string="Fallback record"
    )
    carbon_in_value_origin = fields.Char(string="Value origin", readonly=True)

    carbon_in_use_distribution = fields.Boolean(
        default=False, string="Use Distribution", help="Todo: add help"
    )
    carbon_in_distribution_line_ids = fields.One2many(
        "carbon.distribution.line",
        "res_id",
        "Distribution lines IN",
        auto_join=True,
        domain="[('carbon_type', '=', 'in')]",
    )
    carbon_in_has_valid_distribution = fields.Boolean(
        compute="_compute_carbon_in_has_valid_distribution"
    )

    # --------------------------------------------
    #                   Sales value
    # --------------------------------------------
    carbon_out_is_manual = fields.Boolean(default=False)
    carbon_out_mode = fields.Selection(
        selection=[
            ("auto", "Automatic"),
            ("manual", "Manual"),
        ],
        default="auto",
        compute="_compute_carbon_out_mode",
        store=True,
    )
    carbon_out_factor_id = fields.Many2one(
        "carbon.factor",
        string="Emission Factor Sales",
        ondelete="set null",
        domain="[('id', 'in', carbon_allowed_factor_ids)]",
    )
    carbon_out_fallback_reference = fields.Reference(
        selection="_selection_fallback_model", readonly=True, string="Fallback record "
    )
    carbon_out_value_origin = fields.Char(string="Value origin ", readonly=True)

    carbon_out_use_distribution = fields.Boolean(
        default=False, string="Use Distribution "
    )
    carbon_out_distribution_line_ids = fields.One2many(
        "carbon.distribution.line",
        "res_id",
        "Distribution lines OUT",
        auto_join=True,
        domain="[('carbon_type', '=', 'out')]",
    )
    carbon_out_has_valid_distribution = fields.Boolean(
        compute="_compute_carbon_out_has_valid_distribution"
    )

    # --------------------------------------------
    #            COMPUTE (+related methods)
    # --------------------------------------------

    def _compute_carbon_allowed_factor_ids(self):
        """We use a non stored compute field on purpose so it is dynamically computed on each model thanks to _get_available_carbon_compute_methods()"""
        self.carbon_allowed_factor_ids = self.get_allowed_factors()

    def _compute_model_name(self):
        for record in self:
            record.model_name = record._name

    @api.depends("carbon_in_distribution_line_ids.percentage")
    def _compute_carbon_in_has_valid_distribution(self):
        for record in self:
            record.carbon_in_has_valid_distribution = (
                record.has_valid_carbon_distribution("in")
            )

    @api.depends("carbon_out_distribution_line_ids.percentage")
    def _compute_carbon_out_has_valid_distribution(self):
        for record in self:
            record.carbon_out_has_valid_distribution = (
                record.has_valid_carbon_distribution("out")
            )

    """
    It is possible to override the 2 following methods with some rules
        - The override should call super() or at least the abstract method correctly
        - You can add depends to trigger changes for records in 'auto' mode
        - Don't use general depends, use carbon fields even if you have to add a lot. E.g
            GOOD > @api.depends('product_tmpl_id.carbon_value', 'product_tmpl_id.carbon_in_compute_method', etc...)
            BAD  > @api.depends('product_tmpl_id')
            common related fields are: 'value', 'compute_method', 'uom_id', 'monetary_currency_id'
    """

    @api.depends("carbon_in_is_manual")
    def _compute_carbon_in_mode(self):
        self._compute_carbon_mode("in")

    @api.depends("carbon_out_is_manual")
    def _compute_carbon_out_mode(self):
        self._compute_carbon_mode("out")

    def _compute_carbon_mode(self, carbon_type: str):
        for rec in self:
            if rec[f"carbon_{carbon_type}_is_manual"]:
                mode = "manual"
                fallback_record = False
                origin = _("Manual")
            else:
                mode = "auto"
                fallback_path = rec._search_fallback_record(carbon_type)
                if fallback_path:
                    fallback_record = fallback_path[-1]
                    origin = rec.generate_origin_string(fallback_path, carbon_type)
                else:
                    fallback_record = False
                    origin = _(
                        "No fallback found for this record (company value will be used instead)"
                    )

            rec.update(
                {
                    f"carbon_{carbon_type}_mode": mode,
                    f"carbon_{carbon_type}_fallback_reference": fallback_record,
                    f"carbon_{carbon_type}_value_origin": origin,
                }
            )

    """
    Override these methods to add fallback records to search for carbon values
        > e.g. on product.product, get factor from template or category if record value is not valid
    Order matters, you can insert a record where it fits the most
    """

    def _get_carbon_in_fallback_records(self) -> list[Any]:
        if not self:
            return []
        self.ensure_one()
        return []

    def _get_carbon_out_fallback_records(self) -> list[Any]:
        if not self:
            return []
        self.ensure_one()
        return []

    def _search_fallback_record(self, carbon_type: str) -> list[Any] | None:
        """
        Build the list of possible fallback records, then search the first valid one
        :return: a list with the path to the first valid record
        """
        if not self:
            return []
        self.ensure_one()
        fallback_path = []
        for rec in self._build_fallback_records_list(carbon_type):
            # skip unsaved records with temporary IDs
            if not rec.id or isinstance(rec.id, str) and rec.id.startswith("NewId"):
                continue
            fallback_path.append(rec)
            if rec.has_valid_carbon_value(carbon_type):
                return fallback_path
        return None

    def _build_fallback_records_list(self, carbon_type: str) -> list:
        """
        Recursively build a list with all possible fallback records.
        Ex:
            A.fallback_records = [B, C]
            B.fallback_records = [D]
            C.fallback_records = [B]
            D.fallback_records = []

            A._build_fallback_records_list() -> [B, C, D]

        :return: a list with correctly sorted records.
        """
        # Get fallback records and filter to remove falsy records (e.g. don't add parent if parent_id is False)
        valid_fallback_records = list(
            filter(
                None,
                getattr(
                    self, f"_get_carbon_{carbon_type}_fallback_records", lambda: list()
                )(),
            )
        )
        # Build the final list with recursive fallback
        fallback_with_recursive = valid_fallback_records.copy()
        for rec in valid_fallback_records:
            # We can't use set as order is important. Might be possible to find another way to do that
            fallback_with_recursive.extend(
                [
                    e
                    for e in rec._build_fallback_records_list(carbon_type)
                    if e not in fallback_with_recursive
                ]
            )
        return fallback_with_recursive

    @api.model
    def generate_origin_string(self, path: list[Any], carbon_type: str) -> str:
        str_path = " > ".join([rec._get_record_description() for rec in path])
        str_path += " > " + path[-1][f"carbon_{carbon_type}_factor_id"].name
        return str_path

    # --------------------------------------------
    #               GENERAL METHODS
    # --------------------------------------------

    def _get_record_description(self) -> str:
        if not self:
            return ""
        self.ensure_one()
        return self._description + (f": {self.name}" if hasattr(self, "name") else "")

    def auto_carbon_distribution(self, carbon_types: list[str] = None):
        # Avoid recursion
        if self.env.context.get("auto_carbon_distribution"):
            return
        carbon_types = carbon_types if carbon_types is not None else self._carbon_types
        # carbon_types might be null (if empty list [] is passed from write method), in that case we just return
        if not carbon_types:
            return
        lines_vals_list = []
        self = self.with_context(auto_carbon_distribution=True)
        for record in self:
            for carbon_type in carbon_types:
                if (
                    record[f"carbon_{carbon_type}_is_manual"]
                    and not record[f"carbon_{carbon_type}_use_distribution"]
                ):
                    if factor := record[f"carbon_{carbon_type}_factor_id"]:
                        record._get_distribution_lines(carbon_type).unlink()
                        lines_vals_list.append(
                            {
                                "factor_id": factor.id,
                                "carbon_type": carbon_type,
                                "percentage": 1,
                                "res_model": record._name,
                                "res_id": record.id,
                            }
                        )

                    else:
                        raise UserError(
                            _(
                                "Missing carbon factor for %s (carbon type: %s)",
                                record._get_record_description(),
                                carbon_type,
                            )
                        )
        self.env["carbon.distribution.line"].create(lines_vals_list)

    # --------------------------------------------
    #                   CRUD
    # --------------------------------------------

    def write(self, vals):
        res = super().write(vals)
        # We only recompute values for carbon types that have been modified
        carbon_types = [
            carbon_type
            for carbon_type in self._carbon_types
            if f"carbon_{carbon_type}_factor_id" in vals
        ]
        self.auto_carbon_distribution(carbon_types=carbon_types)
        return res

    def create(self, vals):
        res = super().create(vals)
        res.auto_carbon_distribution()
        return res

    # --------------------------------------------
    #                   HELPERS
    # --------------------------------------------

    # Note by GCA: I don't know why we have to filter distribution lines, but there is a bug:
    # If we don't filter lines, they all get returned (in & out), whatever the carbon type
    # It seems that the domain in the one2many field is not working as expected...
    def _get_distribution_lines(self, carbon_type: str):
        return self[f"carbon_{carbon_type}_distribution_line_ids"].filtered(
            lambda x: x.carbon_type == carbon_type
        )

    def has_valid_carbon_value(self, carbon_type: str):
        if not self:
            return False
        self.ensure_one()
        return self[
            f"carbon_{carbon_type}_is_manual"
        ] and self.has_valid_carbon_distribution(carbon_type)

    def has_valid_carbon_distribution(self, carbon_type: str):
        if not self:
            return False
        self.ensure_one()
        total_percentage = sum(
            [line.percentage for line in self._get_distribution_lines(carbon_type)]
        )
        return total_percentage == 1

    def has_valid_carbon_fallback(self, carbon_type: str):
        if not self:
            return False
        self.ensure_one()
        return self[f"carbon_{carbon_type}_fallback_reference"] and self[
            f"carbon_{carbon_type}_fallback_reference"
        ].has_valid_carbon_value(carbon_type)

    def can_compute_carbon_value(self, carbon_type: str) -> bool:
        if not self:
            return False
        self.ensure_one()
        return self.has_valid_carbon_value(
            carbon_type
        ) or self.has_valid_carbon_fallback(carbon_type)

    def get_carbon_distribution(
        self, carbon_type: str
    ) -> tuple[CarbonFactor, dict[CarbonFactor, float], str]:
        """Return factors and their distributions for a given carbon type"""
        if not self:
            return ()
        self.ensure_one()
        lines = self[f"carbon_{carbon_type}_distribution_line_ids"]
        return (
            lines.factor_id,
            {line.factor_id: line.percentage for line in lines},
            self.model_name,
        )

    def carbon_widget_update_field(self, field_name: str, value: Any):
        field = getattr(self, field_name)
        if isinstance(field, models.BaseModel) and isinstance(value, list):
            value = value[0]
        self.write({field_name: value})

    # --------------------------------------------
    #                   ACTIONS
    # --------------------------------------------

    # def action_see_carbon_origin(self):
    #     """
    #     Pass `carbon_type` in context to ask for a value origin (e.g. 'carbon_value' will show 'carbon_value_origin' to user)
    #     Nice to have: save model and res_id in _compute_carbon_value to add a link to value origin
    #     """
    #     self.ensure_one()
    #     default_carbon_type = "carbon_in"
    #
    #     # I think we are traceback proof here..............
    #     carbon_type = self.env.context.get("carbon_type", default_carbon_type)
    #     if not hasattr(self, carbon_type):
    #         carbon_type = default_carbon_type
    #     origin = getattr(self, f"{carbon_type}_value_origin")
    #     carbon_value = round(
    #         getattr(self, f"{carbon_type}_value"), 4
    #     )  # Quick fix for weird rounding (hoping it will stay the same)
    #
    #     return {
    #         "type": "ir.actions.client",
    #         "tag": "display_notification",
    #         "params": {
    #             "title": _("CO2e Value: %s Kg", carbon_value),
    #             "message": origin or _("No CO2e origin for this record"),
    #             "type": "info",
    #             "sticky": False,
    #             "next": {"type": "ir.actions.act_window_close"},
    #         },
    #     }
