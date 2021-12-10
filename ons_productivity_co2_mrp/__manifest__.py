# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License OPL-1 or later (https://www.odoo.com/documentation/14.0/legal/licenses.html#odoo-apps).

{
    "name": "CO2 MRP",
    "version": "1.0",
    "author": "Open Net Sàrl",
    "category": "Extra Tools",
    "website": "https://www.open-net.ch",
    "summary": "CO2 manufacturing tracking",
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
        "views/mrp_bom.xml",
        "views/mrp_production.xml",
        "views/product_template.xml",
    ],
    "images": [
        "static/description/co2_mrp_green.png",
    ],
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "sequence": 4,
}
