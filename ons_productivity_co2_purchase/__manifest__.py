# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CO2 Purchase",
    "version": "1.0",
    "author": "Open Net Sàrl",
    "category": "Extra Tools",
    "website": "https://www.open-net.ch",
    "summary": "Track your purchased CO2",
    "description": """
Description
**********************



""",
    "depends": [
        "purchase",
        "ons_productivity_co2_account",
    ],
    "data": [
        # Views
        "views/purchase_order.xml",
    ],
    "images": [
        "static/description/co2_purchase_green.png",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "sequence": 3,
}
