# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License OPL-1 or later (https://www.odoo.com/documentation/14.0/legal/licenses.html#odoo-apps).

{
    "name": "CO2 Stock",
    "version": "1.0",
    "author": "Open Net Sàrl",
    "category": "Extra Tools",
    "website": "https://www.open-net.ch",
    "summary": "Base module to support CO2 on stock moves",
    "description": """
Description
**********************



""",
    "depends": [
        "stock",
        "ons_productivity_co2_account",
    ],
    "data": [
        # Views
    ],
    "images": [
        "static/description/co2_stock_green.png",
    ],
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "sequence": 3,
}
