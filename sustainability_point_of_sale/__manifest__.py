{
    "name": "Sustainability Point of Sale",
    "category": "Sales/Point of Sale",
    "version": "18.0.1.0.0",
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
    "author": "MCO2, Open Net Sàrl",
    "maintainers": ["jacopobacci"],
    "development_status": "Production/Stable",
    "website": "https://github.com/sustainability-suite/sustainability-odoo",
    "depends": ["sustainability", "point_of_sale"],
    "assets": {
        "point_of_sale._assets_pos": [
            "sustainability_point_of_sale/static/src/**/*",
        ],
    },
    "sequence": 1,
}
