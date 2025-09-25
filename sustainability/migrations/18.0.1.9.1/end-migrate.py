from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)

    energy_categ = env.ref("sustainability.uom_categ_energy")
    uom_ids = energy_categ.uom_ids

    external_ids = uom_ids.get_external_id()

    for uom in uom_ids:
        external_id = external_ids[uom.id]
        if not external_id:
            continue
        util.update_record_from_xml(cr, xmlid=external_id)
