# © 2025 Open Net Sarl
# License LGPL-3 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sustainability CH HR Payroll ELM Transmission",
    "version": "18.0.1.0.0",
    "author": "MCO2, Open Net Sàrl",
    "maintainers": ["bonnetadam"],
    "development_status": "Production/Stable",
    "category": "Accounting/Sustainability",
    "website": "https://github.com/sustainability-suite/sustainability-odoo",
    "summary": "Allow to see the commuting settings in the employee form when the module l10n_ch_hr_payroll_elm_transmission is installed",
    "depends": [
        "sustainability_employee_commuting",
        "l10n_ch_hr_payroll_elm_transmission",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
    "license": "LGPL-3",
}
