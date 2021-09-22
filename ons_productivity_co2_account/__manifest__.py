# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License OPL-1 or later (https://www.odoo.com/documentation/14.0/legal/licenses.html#odoo-apps).

{
    "name": "CO2 Account",
    "version": "1.0",
    "author": "Open Net Sàrl",
    "category": "Extra Tools",
    "website": "https://www.open-net.ch",
    "summary": "CO2 Accounting",
    "description": """
Description
**********************


""",
    "depends": [
        "account",
        "ons_productivity_co2",
    ],
    "data": [
        # Data
        "data/res_currency.xml",
        # Views
        "views/account_account.xml",
        "views/account_move.xml",
        "views/account_analytic_line.xml",
        "reports/report_invoice_document.xml",
        "views/res_config_settings.xml",
    ],
    "images": [
        "static/description/co2_account_green.png",
    ],
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "sequence": 2,
}
