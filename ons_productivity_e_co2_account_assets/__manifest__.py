# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License OPL-1 or later (https://www.odoo.com/documentation/14.0/legal/licenses.html#odoo-apps).

{
    "name": "CO2 Account Assets",
    "version": "1.0",
    "author": "Open Net Sàrl",
    "category": "Extra Tools",
    "website": "https://www.open-net.ch",
    "summary": "Module allowing CO2 over deprecations",
    "description": """
Description
**********************

""",
    "depends": [
        "account_asset",
        "ons_productivity_co2_account",
    ],
    "data": [
        # Views
        "views/account_asset.xml",
    ],
    "images": [
        "static/description/co2_account_assets_green.png",
    ],
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "sequence": 3,
}
