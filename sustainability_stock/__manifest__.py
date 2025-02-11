{
    "name": "Sustainability Inventory",
    "category": "Inventory/Inventory",
    "version": "17.0.1.0.0",
    "author": "MCO2, Open Net Sàrl",
    "maintainers": ["jacopobacci"],
    "development_status": "Production/Stable",
    "website": "https://github.com/sustainability-suite/sustainability-odoo",
    "depends": ["sustainability", "stock", "stock_delivery"],
    "data": [
        "views/res_config_settings.xml",
        "views/stock_picking.xml",
        "views/carbon_line_origin.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "AGPL-3",
}
