# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License OPL-1 or later (https://www.odoo.com/documentation/14.0/legal/licenses.html#odoo-apps).

{
    "name": "Open Net Productivity: CO2 MRP",
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
        "mrp_account",  # Avec juste mrp: Invalid field 'show_valuation'
        "ons_productivity_co2_stock",
    ],
    "data": [
        # Views
        "views/mrp_production.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "sequence": 4,
}
