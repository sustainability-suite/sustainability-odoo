# © 2023 Open Net Sarl

{
    "name": "CO2 Employee Commuting",
    "version": "17.0.1.0.0",
    "author": "Open Net Sàrl",
    "maintainers": ["bonnetadam"],
    "development_status": "Production/Stable",
    "category": "Accounting/Sustainability",
    "website": "https://www.open-net.ch",
    "summary": "Module for employee commuting co2",
    "description": """Module allowing the calculation of CO2 emissions from employee commuting""",
    "depends": [
        "sustainability",
        "hr_contract",
    ],
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
