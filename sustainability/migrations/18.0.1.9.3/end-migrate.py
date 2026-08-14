from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, Command, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    energy_categ = env.ref("sustainability.uom_categ_energy", raise_if_not_found=False)
    new_reference_uom = env.ref("sustainability.uom_mj", raise_if_not_found=False)
    old_reference_uom = env.ref("sustainability.uom_joule", raise_if_not_found=False)

    if not energy_categ or not new_reference_uom or not old_reference_uom:
        return

    energy_categ.write(
        {
            "uom_ids": [
                Command.update(
                    new_reference_uom.id, {"uom_type": "reference", "factor": 1}
                ),
                Command.update(
                    old_reference_uom.id, {"uom_type": "smaller", "factor": 1000000}
                ),
            ],
            "reference_uom_id": new_reference_uom.id,
        }
    )

    # Re-apply the XML definitions so every energy unit is expressed against the
    # new reference. "init_no_create" only touches records already in database.
    openupgrade.load_data(
        env,
        "sustainability",
        "migrations/18.0.1.9.3/energy_uom.xml",
        mode="init_no_create",
    )
