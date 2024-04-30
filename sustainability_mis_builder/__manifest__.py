# © 2023 Open Net Sarl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sustainability MIS Builder",
    "summary": "Provide CO2 accounting lines data for MIS builder reports",
    "version": "16.0.0.1.0",
    "author": "Open Net Sàrl, Julien Guenat",
    "category": "Accounting/Sustainability",
    "website": "https://www.open-net.ch",
    "depends": ["mis_builder", "sustainability"],
    "data": [
        "views/mis_carbon_account_move_line.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
