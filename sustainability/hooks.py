# © 2026 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from collections.abc import Iterable
from dataclasses import dataclass

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


# ---------------------------------------
# Re-usable utilities for modules that contribute carbon mixins or fields
# => to be called from their pre_init_hook.
@dataclass
class OpenupgradeField:
    """Self-documenting spec for openupgrade.add_fields.

    add_fields consumes each spec positionally (vals[0]..vals[6]); ``__iter__``
    yields the values in that exact order. The dataclass field *declaration*
    order is deliberately different so that ``table`` and ``sql_type`` can carry
    defaults without forcing one onto ``module`` (which must stay required).
    """

    name: str
    model: str
    field_type: str
    module: str
    init_value: object = None  # None/falsy -> add_fields adds no DEFAULT
    table: object = False  # add_fields resolves env[model]._table when False
    sql_type: object = False  # add_fields auto-detects from field_type when False

    def __iter__(self):
        yield from (
            self.name,
            self.model,
            self.table,
            self.field_type,
            self.sql_type,
            self.module,
            self.init_value,
        )


# List of stored fields defined by carbon mixins,
#   keyed by mixin name, with field
#
# carbon.common.mixin is intentionally absent:
# its computed fields are all non-stored
CARBON_MIXIN_STORED_FIELDS = {
    "carbon.mixin": {
        # field: (field_type, sql_type, init_value)
        "carbon_in_mode": ("selection", False, "auto"),  # stored computed
        "carbon_out_mode": ("selection", False, "auto"),  # stored computed
        "carbon_in_is_manual": ("boolean", False, None),
        "carbon_out_is_manual": ("boolean", False, None),
        "carbon_in_use_distribution": ("boolean", False, None),
        "carbon_out_use_distribution": ("boolean", False, None),
    },
    "carbon.line.mixin": {
        "carbon_debt": ("monetary", False, 0.0),  # stored computed
        "carbon_uncertainty_value": ("monetary", False, 0.0),  # stored computed
        "carbon_origin_json": ("json", "jsonb", None),  # stored computed
        "carbon_data_uncertainty_percentage": ("float", "double precision", 0.0),
        "carbon_is_locked": ("boolean", False, None),
    },
}


def _carbon_mixin_fields_spec(
    model_name, mixin_name, module
) -> Iterable[OpenupgradeField]:
    """Expand ``(model, mixin)`` pairs into OpenupgradeField specs for `module`.

    :param models: iterable of ``(model_name, mixin_name)`` tuples
    :param module: technical name of the module that owns these fields (used by
        add_fields for the ir.model.data xml-id)
    """
    mixin_fields = CARBON_MIXIN_STORED_FIELDS.get(mixin_name)
    if not mixin_fields:
        _logger.warning(
            "No stored fields known for mixin %s (model %s), skipped",
            mixin_name,
            model_name,
        )
        return
    for name, (field_type, sql_type, init_value) in mixin_fields.items():
        yield OpenupgradeField(
            name=name,
            model=model_name,
            field_type=field_type,
            module=module,
            init_value=init_value,
            sql_type=sql_type,
        )


def carbon_mixin_fields_spec(models, module):
    """Expand ``(model, mixin)`` pairs into OpenupgradeField specs for `module`.

    :param models: iterable of ``(model_name, mixin_name)`` tuples
    :param module: technical name of the module that owns these fields (used by
        add_fields for the ir.model.data xml-id)
    """
    return [
        field_spec
        for model_name, mixin_name in models
        for field_spec in _carbon_mixin_fields_spec(model_name, mixin_name, module)
    ]


def add_fields(env, fields_spec: Iterable[OpenupgradeField]):
    """Utility to add fields

    :param env: the environment passed to the pre_init_hook
    :param fields_spec: iterable of OpenupgradeField (or any 7-slot sequence)
    """
    # We just wrap openupgrade.add_fields for now.
    # The method is legacy and could be done directly in SQL
    openupgrade.add_fields(env, [tuple(spec) for spec in fields_spec])


# ---------------------------------------


def carbon_fields_spec():
    # Stored fields defined directly on the models (not via a mixin).
    _fields_spec = [
        ("carbon_balance", "account.move"),
        ("carbon_uncertainty_value", "account.move"),
        ("carbon_balance", "account.move.line"),
        ("carbon_debit", "account.move.line"),
        ("carbon_credit", "account.move.line"),
    ]
    return [
        OpenupgradeField(field, model, "monetary", "sustainability", init_value=0.0)
        for field, model in _fields_spec
    ]


# Concrete models the core module contributes a carbon mixin to.
CARBON_MIXIN_MODELS = [
    ("res.company", "carbon.mixin"),
    ("res.partner", "carbon.mixin"),
    ("account.account", "carbon.mixin"),
    ("product.category", "carbon.mixin"),
    ("product.product", "carbon.mixin"),
    ("product.template", "carbon.mixin"),
    ("product.supplierinfo", "carbon.mixin"),
    ("res.country", "carbon.mixin"),
    ("account.move.line", "carbon.line.mixin"),
]


def pre_init_hook(env):
    """Allow installing Sustainability in large databases (>1M records)"""
    fields_spec = []
    fields_spec += carbon_mixin_fields_spec(CARBON_MIXIN_MODELS, "sustainability")
    fields_spec += carbon_fields_spec()

    add_fields(env, fields_spec)
