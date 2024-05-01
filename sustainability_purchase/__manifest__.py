{
    "name": "Sustainability Purchase",
    "version": "16.0.1.3.0",
    "author": "Open Net Sàrl, Gautier Casabona",
    "category": "Accounting/Sustainability",
    "website": "https://www.open-net.ch",
    "summary": "Glue module for sustainability & purchase modules",
    "description": """ This module can be activated from Sustainability settings to add CO2e tracking on purchase orders. """,
    "depends": [
        "sustainability",
        "purchase",
    ],
    "data": [
        # Data
        "data/ir_cron.xml",
        # Views
        # "views/product_supplierinfo.xml",
        "views/carbon_factor.xml",
        "views/carbon_line_origin.xml",
        "views/purchase_order.xml",
        "views/res_partner.xml",
    ],
    "images": [
        "static/description/co2_base_green.png",
    ],
    "installable": False,
    "application": False,
    "auto_install": False,
    "license": "AGPL-3",
    "sequence": 1,
    "pre_init_hook": "add_carbon_mode_columns",
}
