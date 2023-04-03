from odoo import api, fields, models, _
from typing import Any


# DO NOT DELETE
def auto_depends(cls):
    all_fb_rec = getattr(cls, '_fallback_records', list()) + getattr(CarbonMixin, '_fallback_records', list())
    all_fb_rec_fields = getattr(cls, '_fallback_records_fields', list()) + getattr(CarbonMixin, '_fallback_records_fields', list())

    for prefix in ['carbon', 'carbon_sale']:
        fb_rec_fields = [f"{prefix}_{f}" for f in all_fb_rec_fields]
        res = [f"{fr}.{f}" for fr in all_fb_rec for f in fb_rec_fields]
        setattr(cls, f'_compute_{prefix}_value', api.depends(*res)(getattr(cls, f'_compute_{prefix}_value', getattr(CarbonMixin, f'_compute_{prefix}_value'))))

    # cls._compute_carbon_sale_value = api.depends(*res)(getattr(cls, '_compute_carbon_sale_value', getattr(CarbonMixin, '_compute_carbon_sale_value')))
    return cls


# DO NOT DELETE
# def auto_carbon_compute(cls):
#     try:
#         carbon_mixin_class = CarbonMixin
#
#         def __init__(self, env, ids, prefetch_ids):
#             super(cls, self).__init__(env, ids, prefetch_ids)
#             if hasattr(cls, '_fallback_records'):
#                 # Need to copy the method to add
#                 cls._compute_carbon_mode = _auto_depends(carbon_mixin_class, cls, 'carbon')
#                 cls._compute_carbon_sale_mode = _auto_depends(carbon_mixin_class, cls, 'carbon_sale')
#
#         cls.__init__ = __init__
#     except:
#         pass
#     return cls


class CarbonMixin(models.AbstractModel):
    _name = "carbon.mixin"
    _description = "A mixin used to add carbon values on any model"
    _fallback_records = []
    _fallback_records_fields = ['value', 'compute_method', 'uom_id', 'monetary_currency_id']

    _sql_constraints = [
        ('not_negative_carbon_value', 'CHECK(carbon_value >= 0)', 'CO2e value can not be negative !'),
        ('not_negative_carbon_sale_value', 'CHECK(carbon_sale_value >= 0)', 'CO2e value can not be negative !'),
    ]


    # --------------------------------------------
    #               SHARED INFOS
    # --------------------------------------------
    carbon_currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref("onsp_co2.carbon_kilo", False),
    )
    carbon_currency_label = fields.Char(related="carbon_currency_id.currency_unit_label")


    # --------------------------------------------
    #           General/Purchase value
    # --------------------------------------------


    carbon_is_manual = fields.Boolean(default=False)
    carbon_mode = fields.Selection(
        selection=[
            ('auto', 'Automatic'),
            ('manual', 'Manual'),
        ],
        default='auto',
        compute="_compute_carbon_mode",
        store=True,
    )
    carbon_factor_id = fields.Many2one("carbon.factor", string="Emission Factor", ondelete='set null')
    carbon_value = fields.Float(
        string="CO2e value",
        digits="Carbon value",
        help="Used to compute CO2 cost",
        compute="_compute_carbon_value",
        store=True,
        readonly=False,     # Should be readonly in views if carbon_factor_id != False
        recursive=True,     # Only here to prevent
    )
    carbon_compute_method = fields.Selection(
        selection=[
            ('physical', 'Physical'),
            ('monetary', 'Monetary'),
        ],
        string="Compute method",
        default=False,
    )
    carbon_value_origin = fields.Char(compute="_compute_carbon_value", store=True, recursive=True, string="Value origin")
    carbon_uom_id = fields.Many2one("uom.uom")
    carbon_monetary_currency_id = fields.Many2one("res.currency")
    carbon_unit_label = fields.Char(compute="_compute_carbon_unit_label", string=" ")


    # --------------------------------------------
    #                   Sales value
    # --------------------------------------------
    carbon_sale_is_manual = fields.Boolean(default=False)
    carbon_sale_mode = fields.Selection(
        selection=[
            ('auto', 'Automatic'),
            ('manual', 'Manual'),
        ],
        default='auto',
        compute="_compute_carbon_sale_mode",
        store=True,
    )
    carbon_sale_factor_id = fields.Many2one("carbon.factor", string="Emission Factor ", ondelete='set null')
    carbon_sale_value = fields.Float(
        string="CO2e value for sales",
        digits="Carbon value",
        help="Used to compute CO2 cost for sales",
        compute="_compute_carbon_sale_value",
        store=True,
        readonly=False,  # Should be readonly in views if carbon_factor_id != False
        recursive=True,
    )
    carbon_sale_compute_method = fields.Selection(
        selection=[
            ('physical', 'Physical'),
            ('monetary', 'Monetary'),
        ],
        string="Compute method ",
        default=False,
    )
    carbon_sale_value_origin = fields.Char(compute="_compute_carbon_sale_value", store=True, recursive=True, string="Value origin ")
    carbon_sale_uom_id = fields.Many2one("uom.uom")
    carbon_sale_monetary_currency_id = fields.Many2one("res.currency")
    carbon_sale_unit_label = fields.Char(compute="_compute_carbon_sale_unit_label", string="  ")




    @api.depends('carbon_compute_method', 'carbon_monetary_currency_id', 'carbon_uom_id')
    def _compute_carbon_unit_label(self):
        for rec in self:
            rec.carbon_unit_label = "/ " + str(rec.carbon_uom_id.name if rec.carbon_compute_method == 'physical' else rec.carbon_monetary_currency_id.currency_unit_label)

    @api.depends('carbon_sale_compute_method', 'carbon_sale_monetary_currency_id', 'carbon_sale_uom_id')
    def _compute_carbon_sale_unit_label(self):
        for rec in self:
            rec.carbon_sale_unit_label = "/ " + str(rec.carbon_sale_uom_id.name if rec.carbon_sale_compute_method == 'physical' else rec.carbon_sale_monetary_currency_id.currency_unit_label)


    """
    Expected behaviour of co2 settings in standard module:
    
    MANUAL MODE - You have 2 choices:
        1) You can setup everything by yourself: value, method (physical or monetary) and UOM / currency depending on method
        2) You can select a carbon factor to bind parameters to this latter. All updates on carbon factor will impact parameters on record.
        
    AUTO MODE:
        - Odoo will search for a fallback records thanks to these 2 methods:
            1) _get_carbon_value_fallback_records() -> for purchase values or models that only need 1 value (e.g. account.account)
            2) _get_carbon_sale_value_fallback_records() -> for sale values
        - Values from fallback will be copied on records
        - On any update on the fallback record, changes will be copied but you need to add depends on _compute_carbon_mode / _compute_carbon_sale_mode
    """

    @api.depends(
        'carbon_factor_id.carbon_value',
        'carbon_factor_id.carbon_compute_method',
        'carbon_factor_id.carbon_uom_id',
        'carbon_factor_id.carbon_monetary_currency_id',
    )
    def _compute_carbon_value(self):
        self._compute_carbon_value_abstract('carbon')

    @api.depends(
        'carbon_sale_factor_id.carbon_value',
        'carbon_sale_factor_id.carbon_compute_method',
        'carbon_sale_factor_id.carbon_uom_id',
        'carbon_sale_factor_id.carbon_monetary_currency_id',
    )
    def _compute_carbon_sale_value(self):
        self._compute_carbon_value_abstract('carbon_sale')

    def _compute_carbon_value_abstract(self, prefix: str) -> None:
        """
        Abstract method that computes carbon_ and carbon_sale_ prefixed fields
        Will update record only if mode is manual and factor is set
        """
        for rec in self.filtered(f"{prefix}_is_manual"):
            factor = getattr(rec, f"{prefix}_factor_id", None)
            if factor:
                rec._update_carbon_fields(
                    prefix,
                    vals={
                        f"{prefix}_value": factor.carbon_value,
                        f"{prefix}_compute_method": factor.carbon_compute_method,
                        f"{prefix}_uom_id": factor.carbon_uom_id,
                        f"{prefix}_monetary_currency_id": factor.carbon_monetary_currency_id,
                    },
                    origin=factor._get_record_description()
                )

    """
    It is possible to override the 2 following methods with some rules
        - The override should call super() or at least the abstract method correctly
        - You can add depends to trigger changes for records in 'auto' mode
        - Don't use general depends, use carbon fields even if you have to add a lot. E.g
            GOOD > @api.depends('product_tmpl_id.carbon_value', 'product_tmpl_id.carbon_compute_method', etc...)
            BAD  > @api.depends('product_tmpl_id')
            common related fields are: 'value', 'compute_method', 'uom_id', 'monetary_currency_id' 
    """
    @api.depends('carbon_is_manual')
    def _compute_carbon_mode(self):
        self._compute_carbon_mode_abstract('carbon')

    @api.depends('carbon_sale_is_manual')
    def _compute_carbon_sale_mode(self):
        self._compute_carbon_mode_abstract('carbon_sale')

    def _compute_carbon_mode_abstract(self, prefix: str):
        for rec in self:
            if getattr(rec, f"{prefix}_is_manual", False):
                setattr(rec, f"{prefix}_mode", 'manual')
                setattr(rec, f"{prefix}_value_origin", _("Manual"))
            else:
                setattr(rec, f"{prefix}_mode", 'auto')
                fallback_path = rec._search_fallback_record(prefix)
                if fallback_path:
                    fallback_record = fallback_path[-1]
                    origin = rec.generate_origin_string(fallback_path, prefix)
                else:
                    fallback_record = None
                    origin = _("No fallback found for this record (company value will be used instead)")

                rec._update_carbon_fields(prefix, record=fallback_record, origin=origin)




    def _update_carbon_fields(self, prefix: str, vals: dict = None, record: Any = None, origin: str = None):
        """
        Update some fields related to carbon computation, depending on the `prefix` parameter.
        1) if `vals` is not None, record will be ignored (> priority order)
        2) if `vals` is None and `record` is None, fields will be updated with falsy values. Useful if you need to reset them.
        """
        self.ensure_one()
        if vals is None:
            vals = dict()
            for field in ['value', 'compute_method', 'uom_id', 'monetary_currency_id']:
                vals[f"{prefix}_{field}"] = getattr(record, f"{prefix}_{field}", False)
        for field, value in vals.items():
            setattr(self, field, value)
        # We set origin separately to be allowed to put anything in any situation
        if origin is None:
            origin = record._get_record_description() if record else ""
        setattr(self, f"{prefix}_value_origin", origin)




    """
    These methods return True in 2 cases:
        - if value is > 0
        - if an emission factor is defined (which means that the value can be 0)
    """
    def has_valid_carbon_value(self):
        return len(self) == 1 and (
            (self.carbon_compute_method == 'physical' and self.carbon_uom_id) or
            (self.carbon_compute_method == 'monetary' and self.carbon_monetary_currency_id)
        )

    def has_valid_carbon_sale_value(self):
        return len(self) == 1 and (
                (self.carbon_sale_compute_method == 'physical' and self.carbon_sale_uom_id) or
                (self.carbon_sale_compute_method == 'monetary' and self.carbon_sale_monetary_currency_id)
        )

    @api.model
    def generate_origin_string(self, path: list[Any], prefix: str) -> str:
        str_path = " > ".join([rec._get_record_description() for rec in path])
        factor = getattr(path[-1], f"{prefix}_factor_id", None)
        origin = getattr(path[-1], f"{prefix}_value_origin", None)
        if factor or origin:
            str_path += " > " + (factor._get_record_description() if factor else origin)
        return str_path

    def _get_record_description(self) -> str:
        self.ensure_one()
        return self._description + (f": {self.name}" if hasattr(self, 'name') else "")

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

    def _search_fallback_record(self, prefix: str) -> list[Any]:
        """
        Build the list of possible fallback records, then search the first valid value
        :return: a list with the path to the first valid record
        """
        self.ensure_one()
        field = f"{prefix}_value"
        fallback_records = self._build_fallback_records_list(field)
        fallback_path = []
        for rec in fallback_records:
            fallback_path.append(rec)
            if getattr(rec, f"{prefix}_mode") == 'manual' and getattr(rec, f"has_valid_{field}")():
                return fallback_path
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
        carbon_type = self.env.context.get('carbon_type', 'carbon')
        if not hasattr(self, f"{carbon_type}_value"):
            return {}

        getattr(self, f"_compute_{carbon_type}_mode")()
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
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }



