{
    "name": "CO2 Purchase",
    "version": "16.0.1.0.0",
    "author": "Open Net Sàrl",
    "category": "hidden",
    "website": "https://www.open-net.ch",
    "summary": "Glue module for co2 & purchase modules",
    "description": """ AAA """,
    "depends": [
        "onsp_co2",
        "purchase",
    ],
    "data": [
        # Views
        "views/product_supplierinfo.xml",
        "views/purchase_order.xml",
        "views/res_partner.xml",
    ],
    "images": [
        "static/description/co2_base_green.png",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
    "license": "AGPL-3",
    "sequence": 1,
}
