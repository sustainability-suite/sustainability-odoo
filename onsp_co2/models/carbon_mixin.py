from odoo import api, fields, models, _
from typing import Any


class CarbonMixin(models.AbstractModel):
    _name = "carbon.mixin"
    _description = "A mixin used to add carbon values on any model"

    _sql_constraints = [
        ('not_negative_carbon_value', 'CHECK(carbon_value >= 0)', 'CO2e value can not be negative !'),
        ('not_negative_carbon_sale_value', 'CHECK(carbon_sale_value >= 0)', 'CO2e value can not be negative !'),
    ]

    # --- General value / Purchase value
    carbon_factor_id = fields.Many2one("carbon.factor", string="Emission Factor")
    carbon_value = fields.Float(
        string="CO2e value",
        digits="Carbon value",
        help="Used to compute CO2 cost",
        compute="_compute_carbon_value",
        store=True,
        readonly=False,     # Should be readonly in views if carbon_factor_id != False
        recursive=True,     # Only here to prevent
    )
    carbon_value_origin = fields.Char(compute="_compute_carbon_value", store=True, recursive=True)

    # --- Sales value
    carbon_sale_factor_id = fields.Many2one("carbon.factor", string="Sale Emission Factor")
    carbon_sale_value = fields.Float(
        string="CO2e value for sales",
        digits="Carbon value",
        help="Used to compute CO2 cost for sales",
        compute="_compute_carbon_sale_value",
        store=True,
        readonly=False,  # Should be readonly in views if carbon_factor_id != False
        recursive=True,
    )
    carbon_sale_value_origin = fields.Char(compute="_compute_carbon_sale_value", store=True, recursive=True)


    # Todo: add manual origin onchange


    """
    These methods return True in 2 cases:
        - if value is > 0
        - if an emission factor is defined (which means that the value can be 0)
    """
    def has_valid_carbon_value(self):
        return len(self) == 1 and (self.carbon_factor_id or self.carbon_value)

    def has_valid_carbon_sale_value(self):
        return len(self) == 1 and (self.carbon_sale_factor_id or self.carbon_sale_value)


    """
    It is possible to override the 2 following methods but be careful:
        - The override should call super() or at least the abstract method correctly
        - Adding depends could lead to unexpected behaviour, especially if value computation is triggered when it shouldn't
    Expected behaviour in standard module:
        - Only carbon factor (or its value) updates will trigger an automatic computation
        - Manual computation is still possible on a record (with an action/button)
        - Fallback records shouldn't trigger these methods
    """
    @api.depends('carbon_factor_id.carbon_value')
    def _compute_carbon_value(self):
        self._compute_carbon_value_abstract('carbon')

    @api.depends('carbon_sale_factor_id.carbon_value')
    def _compute_carbon_sale_value(self):
        self._compute_carbon_value_abstract('carbon_sale')

    def _compute_carbon_value_abstract(self, prefix: str) -> None:
        """
        Abstract method that computes carbon_ and carbon_sale_ prefixed fields
        Carbon value should be taken from the record, but we compute it if the factor changes
        """
        for rec in self:
            factor = getattr(rec, f"{prefix}_factor_id", None)
            if factor:
                setattr(rec, f"{prefix}_value", factor.carbon_value)
                setattr(rec, f"{prefix}_value_origin", factor._get_record_description())
            else:
                fallback_path = rec._search_fallback_record(f"{prefix}_value")
                setattr(rec, f"{prefix}_value", getattr(fallback_path[-1], f"{prefix}_value", False))
                setattr(rec, f"{prefix}_value_origin", rec.generate_origin_string(fallback_path, prefix))




    def _get_record_description(self) -> str:
        self.ensure_one()
        return self._description + (f": {self.name}" if hasattr(self, 'name') else "")

    @api.model
    def generate_origin_string(self, path: list[Any], prefix: str) -> str:
        str_path = " > ".join([rec._get_record_description() for rec in path])
        factor = getattr(path[-1], f"{prefix}_factor_id", None)
        origin = getattr(path[-1], f"{prefix}_value_origin", None)
        if factor or origin:
            str_path += " > " + (factor._get_record_description() if factor else origin)
        return str_path

    """
    Override these methods to add fallback records to search for carbon values
    > e.g. on product.product, get factor from template or category if record value is not valid
    Order matters, you can insert a record where it fits the most
    """
    def _get_carbon_value_fallback_records(self) -> list[Any]:
        self.ensure_one()
        return []

    def _get_carbon_sale_value_fallback_records(self) -> list[Any]:
        self.ensure_one()
        return []

    def _search_fallback_record(self, field: str) -> list[Any]:
        """
        Build the list of possible fallback records, then search the first valid value
        :return: a list with the path to the first valid record
        """
        self.ensure_one()
        fallback_records = self._build_fallback_records_list(field)
        fallback_path = []
        for rec in fallback_records:
            fallback_path.append(rec)
            if getattr(rec, f"has_valid_{field}")():
                return fallback_path
        # As an ultimate fallback, take the record company (or current user company)
        fallback_path.append(getattr(self, 'company_id', None) or self.env.company)
        return fallback_path

    def _build_fallback_records_list(self, field: str) -> list:
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
        valid_fallback_records = list(filter(None, getattr(self, f"_get_{field}_fallback_records", lambda: list())()))
        # Build the final list with recursive fallback
        fallback_with_recursive = valid_fallback_records.copy()
        for rec in valid_fallback_records:
            # We can't use set as order is important. Might be possible to find another way to do that
            fallback_with_recursive.extend([e for e in rec._build_fallback_records_list(field) if e not in fallback_with_recursive])
        return fallback_with_recursive





    # --------------------------------------------
    #                   ACTIONS
    # --------------------------------------------


    def action_recompute_carbon(self):
        searched_value = self.env.context.get('carbon_value_name', 'carbon_value')
        if not hasattr(self, searched_value):
            return {}

        getattr(self, f"_compute_{searched_value}")()
        return self.action_see_carbon_origin() if len(self) == 1 else {}

    def action_see_carbon_origin(self):
        """
            Pass `carbon_value_name` in context to ask for a value origin (e.g. 'carbon_value' will show 'carbon_value_origin' to user)
            Nice to have: save model and res_id in _compute_carbon_value to add a link to value origin
        """
        self.ensure_one()

        # I think we are traceback proof here..............
        searched_value = self.env.context.get('carbon_value_name', 'carbon_value')
        if not hasattr(self, searched_value):
            searched_value = 'carbon_value'
        origin = getattr(self, f"{searched_value}_origin")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': f"CO2e Value: {round(getattr(self, searched_value), 4)}",      # Quick fix for weird rounding (hoping it will stay the same)
                'message': origin or _("No CO2e origin for this record"),
                'type': 'info',
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }



