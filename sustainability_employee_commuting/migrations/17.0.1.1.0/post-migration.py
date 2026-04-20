from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})

    commuting_records = env['carbon.hr.commuting'].search([])
    for record in commuting_records:
        record.start_date = record.create_date
