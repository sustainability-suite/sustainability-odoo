# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CO2 Tracking Base",
    "version": "1.0",
    "author": "Open Net Sàrl",
    "category": "hidden",
    "website": "https://www.open-net.ch",
    "summary": "Base module to track your CO2 debts",
    "description": """
Description
**********************



""",
    "depends": [
        "product",
    ],
    "data": [
        # Views
        "views/product_template.xml",
        "views/product_product.xml",
        "views/product_category.xml",
        "views/res_partner.xml",
        "views/product_supplierinfo.xml",
        "views/res_country.xml",
        "views/res_company.xml",
    ],
    "images": [
        "static/description/co2_base_green.png",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "sequence": 1,
}
