from odoo.addons.sustainability.hooks import OpenupgradeField, add_fields


def add_carbon_mode_columns(env):
    """Pre_init_hook to avoid performance issues on large databases.

    Two stored fields would otherwise be recomputed across every existing
    record at install:

    * ``stock.picking.carbon_debt`` (stored computed) on the high-volume
      picking table, and
    * ``carbon.line.origin.move_carbon_freight_picking_id`` (stored related),
      which grows ~one row per carbon computation.

    Pre-creating the columns lets Odoo skip the ALTER + recompute backfill.
    See sustainability.hooks.
    """
    add_fields(
        env,
        [
            OpenupgradeField(
                "carbon_debt",
                "stock.picking",
                "monetary",
                "sustainability_stock",
                init_value=0.0,
            ),
            OpenupgradeField(
                "move_carbon_freight_picking_id",
                "carbon.line.origin",
                "many2one",
                "sustainability_stock",
            ),
        ],
    )
