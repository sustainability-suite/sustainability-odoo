# © 2024 Open Net Sarl
# License LGPL-3 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sustainability",
    "version": "18.0.1.2.4",
    "author": "MCO2, Open Net Sàrl",
    "maintainers": ["jguenat", "bonnetadam", "jacopobacci"],
    "development_status": "Production/Stable",
    "category": "Accounting/Sustainability",
    "website": "https://github.com/sustainability-suite/sustainability-odoo",
    "summary": """Base module to track CO2 equivalent in accounting, Sustainability,
     GHG Protocol, CSRD Directive, BEGES, ADEME, ISO format, Action Plan, Emission Factors,
     carbon CO2 footprint computation, Analytical accounting, Decarbonization
    """,
    "depends": [
        "account",
        "web_hierarchy",
    ],
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/account_account.xml",
        "views/account_analytic_line.xml",
        "views/account_move.xml",
        "views/account_move_line.xml",
        "views/carbon_line_origin.xml",
        "views/product_template.xml",
        "views/carbon_factor.xml",
        "views/carbon_factor_database.xml",
        "views/carbon_factor_contributor.xml",
        "views/carbon_factor_type.xml",
        "views/product_category.xml",
        "views/res_country.xml",
        "views/res_config_settings.xml",
        "views/sustainability_scenario.xml",
        "views/sustainability_action_plan.xml",
        "views/sustainability_action.xml",
        "views/sustainability_approach.xml",
        "views/sustainability_nomenclature.xml",
        "views/res_partner.xml",
        # Reports
        "report/invoice_document.xml",
        "report/carbon_factor_value_report_view.xml",
        # Data
        "data/decimal_precision.xml",
        "data/menu_items.xml",
        "data/res_currency.xml",
        "data/uom.xml",
        "data/res_country_group.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
    "demo": [
        "demo/carbon_factor_database.xml",
        "demo/carbon_factor_contributor.xml",
        "demo/carbon_factor_type.xml",
        "demo/carbon_factor.xml",
        "demo/carbon_factor_value.xml",
        "demo/demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sustainability/static/src/js/tours/*.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
    "sequence": 1,
    "pre_init_hook": "_pre_init_carbon",
    "external_dependencies": {
        "python": ["openupgradelib"],
    },
}
