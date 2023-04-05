# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CO2 Tracking Base",
    "version": "16.0.1.0.0",
    "author": "Open Net Sàrl",
    "category": "hidden",
    "website": "https://www.open-net.ch",
    "summary": "Base module to track CO2 equivalent in accounting",
    "description": """
Description
**********************
""",
    "depends": [
        "account",
    ],
    "data": [
        # Security
        "security/ir.model.access.csv",         # todo: Create more roles & access rights

        # Views
        "views/account_account.xml",
        "views/account_analytic_line.xml",
        "views/account_move.xml",
        "views/account_move_line.xml",

        "views/product_template.xml",

        "views/carbon_factor.xml",
        "views/product_category.xml",
        "views/res_country.xml",
        "views/res_config_settings.xml",

        # Reports
        "report/invoice_document.xml",

        # Data
        "data/decimal_precision.xml",
        "data/menu_items.xml",
        "data/res_currency.xml",
    ],
    "images": [
        "static/description/co2_base_green.png",
    ],
    "demo": [
        "demo/carbon_factor.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
    "sequence": 1,
}
