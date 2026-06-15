from odoo.addons.sustainability.hooks import (
    OpenupgradeField,
    add_fields,
    carbon_mixin_fields_spec,
)


def add_carbon_mode_columns(env):
    """Pre_init_hook to avoid performance issues on large databases.

    Two layers of stored carbon fields must be pre-created, otherwise Odoo
    recomputes them across every historical record at install:

    * ``purchase.order.line`` carbon.line.mixin fields (the per-line values), and
    * the ``purchase.order`` aggregates that sum those lines. Pre-creating only
      the lines is not enough: the order-level recompute re-reads every line.

    See sustainability.hooks.add_fields for the rationale.
    """
    fields_spec = carbon_mixin_fields_spec(
        [("purchase.order.line", "carbon.line.mixin")],
        "sustainability_purchase",
    )
    fields_spec += [
        OpenupgradeField(
            "carbon_debt",
            "purchase.order",
            "monetary",
            "sustainability_purchase",
            init_value=0.0,
        ),
        OpenupgradeField(
            "carbon_currency_id",
            "purchase.order",
            "many2one",
            "sustainability_purchase",
        ),
    ]
    add_fields(env, fields_spec)
