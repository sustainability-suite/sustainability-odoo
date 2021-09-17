# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License OPL-1 or later (https://www.odoo.com/documentation/14.0/legal/licenses.html#odoo-apps).

{
    "name": "Open Net Productivity: CO2 Account Assets",
    "version": "1.0",
    "author": "Open Net Sàrl",
    "category": "Extra Tools",
    "website": "https://www.open-net.ch",
    "summary": "Module to install Co2 financial reporting",
    "description": """
Description
**********************
Steps to instal:
    * Install module.
FIX    * Create a currency, warning no update with AFC.
    * Activate the server action "Duplicate financial report".
    * Duplicate financial report (Can be done with all financial report).
    * Open the new financial report, feel free to rename it.
    * Enable boolean field "ons_is_co2_report" and choose your currency.
    * Open normally your co2 financial report.
""",
    "depends": [
        "account_asset",
        "ons_productivity_co2_account",
    ],
    "data": [
        # Views
        "views/account_asset.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "sequence": 3,
}
