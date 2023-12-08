# -*- coding: utf-8 -*-
# © 2023 Open Net Sarl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CO2 : Expense Reports ",
    "summary": "Provide CO2 accounting data for expense reports",
    "version": "16.0.0.1.0",
    "author": "Open-Net Sàrl",
    "category": "Extra Tools",
    "website": "https://www.open-net.ch",
    "depends": ["hr_expense", "onsp_co2"],
    "data": [
        'views/hr_expense.xml',
        'views/hr_expense_sheet.xml'
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
