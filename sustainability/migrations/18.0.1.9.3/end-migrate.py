from odoo import Command
from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)

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

    uom_ids = energy_categ.uom_ids

    external_ids = uom_ids.get_external_id()

    for uom in uom_ids:
        external_id = external_ids[uom.id]
        if not external_id:
            continue
        util.update_record_from_xml(cr, xmlid=external_id)
