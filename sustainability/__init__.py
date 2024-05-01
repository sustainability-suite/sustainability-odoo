# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import models
from . import tests
from odoo import api, SUPERUSER_ID


def migrate_ir_model_data(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from_module = "onsp_co2"
    to_module = "sustainability"

    installed_modules = env["ir.module.module"].search(
        [("name", "ilike", from_module), ("state", "=", "installed")]
    )

    for module in installed_modules.mapped("name"):
        xml_ids = env["ir.model.data"].search([("module", "=", module)])
        xml_ids.write({"module": module.replace(from_module, to_module)})
