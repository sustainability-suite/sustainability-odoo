# © 2023 Open Net Sarl

{
    "name": "Sustainability Employee Commuting",
    "version": "18.0.1.2.0",
    "author": "MCO2, Open Net Sàrl",
    "maintainers": ["bonnetadam", "jacopobacci"],
    "development_status": "Production/Stable",
    "category": "Accounting/Sustainability",
    "website": "https://github.com/sustainability-suite/sustainability-odoo",
    "summary": "Module for employee commuting co2",
    "depends": ["sustainability", "hr_contract", "hr_homeworking"],
    "data": [
        # Data
        "data/ir_cron.xml",
        "data/scheduled_actions.xml",
        # Views
        "views/res_config_settings.xml",
        "views/hr_employee_commuting.xml",
        # Security
        "security/ir.model.access.csv",
    ],
    "images": [
        "static/description/co2_base_green.png",
    ],
    "demo": [
        "data/demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "AGPL-3",
}
