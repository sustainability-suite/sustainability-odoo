# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License OPL-1 or later (https://www.odoo.com/documentation/14.0/legal/licenses.html#odoo-apps).

{
    "name": "Open Net Productivity: CO2 Sale",
    "version": "1.0",
    "author": "Open Net Sàrl",
    "category": "Extra Tools",
    "website": "https://www.open-net.ch",
    "summary": "Module to track your CO2 debts",
    "description": """
Description
**********************



""",
    "depends": [
        "sale",
        "ons_productivity_co2_account",
    ],
    "data": [
        # Views
        "views/sale_order.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "sequence": 3,
}
