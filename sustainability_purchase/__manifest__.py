{
    "name": "Sustainability Purchase",
    "version": "18.0.1.2.1",
    "author": "MCO2, Open Net Sàrl",
    "maintainers": ["jguenat", "bonnetadam", "jacopobacci"],
    "development_status": "Production/Stable",
    "category": "Accounting/Sustainability",
    "website": "https://github.com/sustainability-suite/sustainability-odoo",
    "summary": "Glue module for sustainability & purchase modules",
    "depends": [
        "sustainability",
        "purchase",
    ],
    "data": [
        # Data
        "data/ir_cron.xml",
        # Views
        "views/carbon_factor.xml",
        "views/carbon_line_origin.xml",
        "views/purchase_order.xml",
        "views/res_partner.xml",
        "views/purchase_supplierinfo.xml",
    ],
    "demo": [
        "data/demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "AGPL-3",
    "sequence": 1,
    "pre_init_hook": "add_carbon_mode_columns",
}
