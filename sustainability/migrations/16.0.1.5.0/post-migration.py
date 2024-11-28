from odoo import SUPERUSER_ID, api


def migrate(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    currency = env["res.currency"].search(
        [("name", "=", "KGC"), ("symbol", "=", "KgCO2e")], limit=1
    )

    if currency:
        currency.currency_unit_label = currency.currency_unit_label.replace("Kg", "kg")
        currency.symbol = currency.symbol.replace("Kg", "kg")
        currency.full_name = currency.full_name.replace("Kilogram", "kilogram")
