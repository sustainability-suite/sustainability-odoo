from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from typing import Any


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
APPLICABLE_MODELS = [
    "carbon.factor",
    "product.category",
    "product.product",
    "product.template",
    "res.partner",
    "res.company",
    "res.country",
]



class CarbonMixin(models.AbstractModel):
    _name = "carbon.mixin"
    _description = "A mixin used to add carbon values on any model"
    _fallback_records = []
    _fallback_records_fields = ['value', 'compute_method', 'uom_id', 'monetary_currency_id']

    _sql_constraints = [
        ('not_negative_carbon_in_value', 'CHECK(carbon_in_value >= 0)', 'CO2e value can not be negative !'),
        ('not_negative_carbon_out_value', 'CHECK(carbon_out_value >= 0)', 'CO2e value can not be negative !'),
    ]

    @api.constrains(
        'carbon_in_compute_method', 'carbon_out_compute_method',
        'carbon_in_monetary_currency_id', 'carbon_out_monetary_currency_id',
        'carbon_in_uom_id', 'carbon_out_uom_id',
    )
    def _check_mandatory_fields(self):
        for record in self:
            errors = []
            # IN
            if record.carbon_in_is_manual:
                if record.carbon_in_compute_method == 'monetary' and not record.carbon_in_monetary_currency_id:
                    errors.append(_("You must set a monetary currency for carbon 'in' value"))
                if record.carbon_in_compute_method == 'physical' and not record.carbon_in_uom_id:
                    errors.append(_("You must set a unit of measure for carbon 'in' value"))

            # OUT
            if record.carbon_out_is_manual:
                if record.carbon_out_compute_method == 'monetary' and not record.carbon_out_monetary_currency_id:
                    errors.append(_("You must set a monetary currency for carbon 'out' value"))
                if record.carbon_out_compute_method == 'physical' and not record.carbon_out_uom_id:
                    errors.append(_("You must set a unit of measure for carbon 'out' value"))

            if errors:
                raise ValidationError(_("The following record has missing carbon infos: %s\n\n%s", getattr(record, 'display_name', str(record)), '\n'.join(errors)))

    @api.model
    def _get_available_carbon_compute_methods(self):
        return [
            ('physical', 'Physical'),
            ('monetary', 'Monetary'),
        ]

    @api.model
    def _get_valid_factor_domain(self):
        # Todo: make it dynamic with the _get_available_carbon_compute_methods method
        # For now, users can select a carbon factor with a non authorized compute method
        return "[('carbon_compute_method', '!=', False), ('recent_value_id', '!=', [])]"

    @api.model
    def _selection_fallback_model(self):
        return [
            (x, _(self.env[x]._description)) for x in APPLICABLE_MODELS if x in self.env
        ]

    # --------------------------------------------
    #               SHARED INFOS
    # --------------------------------------------
    carbon_currency_id = fields.Many2one('res.currency', compute="_compute_carbon_currency_id")
    carbon_currency_label = fields.Char(compute="_compute_carbon_currency_id")


    # --------------------------------------------
    #           General/Purchase value
    # --------------------------------------------


    carbon_in_is_manual = fields.Boolean(default=False)
    carbon_in_mode = fields.Selection(
        selection=[
            ('auto', 'Automatic'),
            ('manual', 'Manual'),
        ],
        default='auto',
        compute="_compute_carbon_in_mode",
        store=True,
    )
    carbon_in_factor_id = fields.Many2one("carbon.factor", string="Emission Factor", ondelete='set null', domain=_get_valid_factor_domain)
    carbon_in_value = fields.Float(
        string="CO2e value",
        digits="Carbon value",
        help="Used to compute CO2 cost",
        compute="_compute_carbon_in_value",
        store=True,
        readonly=False,     # Should be readonly in views if carbon_in_factor_id != False
        recursive=True,     # Only here to prevent
    )
    carbon_in_compute_method = fields.Selection(
        selection=_get_available_carbon_compute_methods,
        string="Compute method",
    )
    carbon_in_fallback_reference = fields.Reference(selection="_selection_fallback_model")
    carbon_in_value_origin = fields.Char(compute="_compute_carbon_in_value", store=True, recursive=True, string="Value origin")
    carbon_in_uom_id = fields.Many2one("uom.uom")
    carbon_in_monetary_currency_id = fields.Many2one("res.currency")
    carbon_in_unit_label = fields.Char(compute="_compute_carbon_in_unit_label", string=" ")


    # --------------------------------------------
    #                   Sales value
    # --------------------------------------------
    carbon_out_is_manual = fields.Boolean(default=False)
    carbon_out_mode = fields.Selection(
        selection=[
            ('auto', 'Automatic'),
            ('manual', 'Manual'),
        ],
        default='auto',
        compute="_compute_carbon_out_mode",
        store=True,
    )
    carbon_out_factor_id = fields.Many2one("carbon.factor", string="Emission Factor ", ondelete='set null', domain=_get_valid_factor_domain)
    carbon_out_value = fields.Float(
        string="CO2e value for sales",
        digits="Carbon value",
        help="Used to compute CO2 cost for sales",
        compute="_compute_carbon_out_value",
        store=True,
        readonly=False,  # Should be readonly in views if carbon_in_factor_id != False
        recursive=True,
    )
    carbon_out_compute_method = fields.Selection(
        selection=_get_available_carbon_compute_methods,
        string="Compute method ",
    )
    carbon_out_fallback_reference = fields.Reference(selection="_selection_fallback_model")
    carbon_out_value_origin = fields.Char(compute="_compute_carbon_out_value", store=True, recursive=True, string="Value origin ")
    carbon_out_uom_id = fields.Many2one("uom.uom")
    carbon_out_monetary_currency_id = fields.Many2one("res.currency")
    carbon_out_unit_label = fields.Char(compute="_compute_carbon_out_unit_label", string="  ")



    # --------------------------------------------
    #            COMPUTE (+related methods)
    # --------------------------------------------


    def _compute_carbon_currency_id(self):
        for rec in self:
            rec.carbon_currency_id = self.env.ref("onsp_co2.carbon_kilo", raise_if_not_found=False)
            rec.carbon_currency_label = rec.carbon_currency_id.currency_unit_label

    @api.depends('carbon_in_compute_method', 'carbon_in_monetary_currency_id', 'carbon_in_uom_id')
    def _compute_carbon_in_unit_label(self):
        for rec in self:
            rec.carbon_in_unit_label = "/ " + str(rec.carbon_in_uom_id.name if rec.carbon_in_compute_method == 'physical' else rec.carbon_in_monetary_currency_id.currency_unit_label)

    @api.depends('carbon_out_compute_method', 'carbon_out_monetary_currency_id', 'carbon_out_uom_id')
    def _compute_carbon_out_unit_label(self):
        for rec in self:
            rec.carbon_out_unit_label = "/ " + str(rec.carbon_out_uom_id.name if rec.carbon_out_compute_method == 'physical' else rec.carbon_out_monetary_currency_id.currency_unit_label)


    """
    Expected behaviour of co2 settings in standard module:
    
    MANUAL MODE - You have 2 choices:
        1) You can setup everything by yourself: value, method (physical or monetary) and UOM / currency depending on method
        2) You can select a carbon factor to bind parameters to this latter. All updates on carbon factor will impact parameters on record.
        
    AUTO MODE:
        - Odoo will search for a fallback records thanks to these 2 methods:
            1) _get_carbon_in_value_fallback_records() -> for purchase values or models that only need 1 value (e.g. account.account)
            2) _get_carbon_out_value_fallback_records() -> for sale values
        - Values from fallback will be copied on records
        - On any update on the fallback record, changes will be copied but you need to add depends on _compute_carbon_in_mode / _compute_carbon_out_mode
    """

    @api.depends(
        'carbon_in_factor_id.carbon_value',
        'carbon_in_factor_id.carbon_compute_method',
        'carbon_in_factor_id.carbon_uom_id',
        'carbon_in_factor_id.carbon_monetary_currency_id',
    )
    def _compute_carbon_in_value(self):
        self._compute_carbon_value_abstract('carbon_in')

    @api.depends(
        'carbon_out_factor_id.carbon_value',
        'carbon_out_factor_id.carbon_compute_method',
        'carbon_out_factor_id.carbon_uom_id',
        'carbon_out_factor_id.carbon_monetary_currency_id',
    )
    def _compute_carbon_out_value(self):
        self._compute_carbon_value_abstract('carbon_out')

    def _compute_carbon_value_abstract(self, prefix: str) -> None:
        """
        Abstract method that computes carbon_in_ and carbon_out_ prefixed fields
        Will update record only if mode is manual and factor is set
        """
        for rec in self.filtered(f"{prefix}_is_manual"):
            factor = getattr(rec, f"{prefix}_factor_id", None)
            if factor:
                # Todo: Call a method on carbon factor to get the most recent value and use the value from this latter
                rec._update_carbon_fields(
                    prefix,
                    vals={
                        f"{prefix}_value": factor.carbon_value,
                        f"{prefix}_uom_id": factor.carbon_uom_id,
                        f"{prefix}_monetary_currency_id": factor.carbon_monetary_currency_id,
                        f"{prefix}_compute_method": factor.carbon_compute_method,
                    },
                    origin=factor._get_record_description()
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
    @api.depends('carbon_in_is_manual')
    def _compute_carbon_in_mode(self):
        self._compute_carbon_mode_abstract('carbon_in')

    @api.depends('carbon_out_is_manual')
    def _compute_carbon_out_mode(self):
        self._compute_carbon_mode_abstract('carbon_out')

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
        2) if `record` is not None, this latter will be saved as a reference
        3) if `vals` is None and `record` is None, fields will be updated with falsy values. Useful if you need to reset them.
        """
        self.ensure_one()
        if vals is None:
            vals = dict()
            record_prefix = 'carbon' if record and record._name == 'carbon.factor' else prefix
            for field in ['value', 'uom_id', 'monetary_currency_id', 'compute_method']:
                vals[f"{prefix}_{field}"] = getattr(record, f"{record_prefix}_{field}", False)

            vals[f"{prefix}_fallback_reference"] = record

        for field, value in vals.items():
            setattr(self, field, value)
        # We set origin separately to be allowed to put anything in any situation
        if origin is None:
            origin = record._get_record_description() if record else ""
        setattr(self, f"{prefix}_value_origin", origin)




    """
    Override these methods to add fallback records to search for carbon values
    > e.g. on product.product, get factor from template or category if record value is not valid
    Order matters, you can insert a record where it fits the most
    """
    def _get_carbon_in_value_fallback_records(self) -> list[Any]:
        self.ensure_one()
        return []

    def _get_carbon_out_value_fallback_records(self) -> list[Any]:
        self.ensure_one()
        return []

    def _search_fallback_record(self, prefix: str) -> list[Any]:
        """
        Build the list of possible fallback records, then search the first valid value
        Valid record = manual mode + has_valid_value() == True
        :return: a list with the path to the first valid record
        """
        self.ensure_one()
        field = f"{prefix}_value"
        fallback_records = self._build_fallback_records_list(field)
        fallback_path = []
        for rec in fallback_records:
            fallback_path.append(rec)
            if getattr(rec, f"{prefix}_mode") == 'manual' and getattr(rec, f"has_valid_{field}")():
                if getattr(rec, f"{prefix}_factor_id"):
                    fallback_path.append(getattr(rec, f"{prefix}_factor_id"))
                break
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
    #               GENERAL METHODS
    # --------------------------------------------

    """
    These 2 following methods return True in 2 cases:
        - if value is > 0
        - if an emission factor is defined (which means that the value can be 0)
    Note: could be refactor into a single method with a `prefix` parameter
    """
    def has_valid_carbon_in_value(self):
        return bool(
            len(self) == 1 and (
                (self.carbon_in_compute_method == 'physical' and self.carbon_in_uom_id) or
                (self.carbon_in_compute_method == 'monetary' and self.carbon_in_monetary_currency_id)
            )
        )

    def has_valid_carbon_out_value(self):
        return bool(
            len(self) == 1 and (
                (self.carbon_out_compute_method == 'physical' and self.carbon_out_uom_id) or
                (self.carbon_out_compute_method == 'monetary' and self.carbon_out_monetary_currency_id)
            )
        )

    def get_related_carbon_factor(self, prefix: str):
        """
        If the record is linked to a carbon factor, return this latter. There are 2 scenarios:
            - Either carbon mode is manual and factor_id is set
            - Or carbon mode is auto and the fallback record is a carbon factor
        """
        if getattr(self, f"{prefix}_mode") == 'manual':
            return getattr(self, f"{prefix}_factor_id")
        elif getattr(self, f"{prefix}_mode") == 'auto':
            fallback_record = getattr(self, f"{prefix}_fallback_reference")
            if fallback_record and fallback_record._name == 'carbon.factor':
                return fallback_record
        return None


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




    def get_carbon_value(self, carbon_type: str = None, quantity: float = None, from_uom_id=None, amount: float = None, from_currency_id=None, date=None) -> tuple[float, dict]:
        """
        Return a value computed depending on the calculation method of carbon (qty/price) and the type of operation (credit/debit)
        Used in account.move.line to compute carbon debt if a product is set.
        """
        self.ensure_one()
        if carbon_type not in ['in', 'out']:
            raise UserError(_("Carbon value type must be either 'in' or 'out'"))

        prefix = 'carbon_' + carbon_type
        factor = self.get_related_carbon_factor(prefix)


        if factor:
            # Either mode is manual and factor_id is set or mode is auto and the fallback record is a carbon factor
            infos = factor.get_value_infos_at_date(date)
        else:
            # Either mode is manual and factor_id is False or mode is auto and the fallback record is not a carbon factor
            infos = {
                'compute_method': getattr(self, f"{prefix}_compute_method"),
                'carbon_value': getattr(self, f"{prefix}_value"),
                'carbon_value_origin': getattr(self, f"{prefix}_value_origin"),
                'carbon_uom_id': getattr(self, f"{prefix}_uom_id"),
                'carbon_monetary_currency_id': getattr(self, f"{prefix}_monetary_currency_id"),
            }


        if infos['compute_method'] == "physical" and quantity is not None and from_uom_id:
            if from_uom_id.category_id != infos['carbon_uom_id'].category_id:
                raise ValidationError(_(
                    "The unit of measure chosen for %s (%s - %s) is not in the same category as its carbon unit of measure (%s - %s)\nPlease check the '%s' settings.",
                    self.display_name,
                    from_uom_id.name,
                    from_uom_id.category_id.name,
                    infos['carbon_uom_id'].name,
                    infos['carbon_uom_id'].category_id.name,
                    prefix,
                ))

            value = infos['carbon_value'] * from_uom_id._compute_quantity(quantity, infos['carbon_uom_id'])

        elif infos['compute_method'] == "monetary" and amount is not None and from_currency_id:
            # We convert the amount to the currency used in carbon settings of the record
            date = date or fields.Date.today()
            value = infos['carbon_value'] * from_currency_id._convert(amount, infos['carbon_monetary_currency_id'], self.env.company, date)

        else:
            raise ValidationError(_("To compute a carbon cost, you must pass:"
                              "\n- either a quantity and a unit of measure"
                              "\n- or a price and a currency (+ an optional date)"
                              "\n\nPassed value: "
                              "\n- Record: %s (compute method: %s)"
                              "\n- Quantity: %s, UOM: %s"
                              "\n- Amount: %s, Currency: %s", self, infos['compute_method'], quantity, from_uom_id, amount, from_currency_id))


        return value, infos





    def carbon_widget_update_field(self, field_name: str, value: Any):
        field = getattr(self, field_name)
        if isinstance(field, models.BaseModel) and isinstance(value, list):
            value = value[0]
        self.write({field_name: value})



    # --------------------------------------------
    #                   ACTIONS
    # --------------------------------------------




    def action_recompute_carbon(self, carbon_type: str = None):
        carbon_type = carbon_type or self.env.context.get('carbon_type', 'carbon_in')
        if not hasattr(self, f"{carbon_type}_value"):
            return False

        getattr(self, f"_compute_{carbon_type}_mode")()
        return True

    def action_see_carbon_origin(self):
        """
            Pass `carbon_type` in context to ask for a value origin (e.g. 'carbon_value' will show 'carbon_value_origin' to user)
            Nice to have: save model and res_id in _compute_carbon_value to add a link to value origin
        """
        self.ensure_one()
        default_carbon_type = 'carbon_in'

        # I think we are traceback proof here..............
        carbon_type = self.env.context.get('carbon_type', default_carbon_type)
        if not hasattr(self, carbon_type):
            carbon_type = default_carbon_type
        origin = getattr(self, f"{carbon_type}_value_origin")
        carbon_value = round(getattr(self, f"{carbon_type}_value"), 4)  # Quick fix for weird rounding (hoping it will stay the same)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("CO2e Value: %s Kg", carbon_value),
                'message': origin or _("No CO2e origin for this record"),
                'type': 'info',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }



