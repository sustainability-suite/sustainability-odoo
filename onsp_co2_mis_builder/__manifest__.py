# © 2023 Open Net Sarl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Open Net Productivity: CO2 MIS Builder",
    "summary": "Provide CO2 accounting lines data for MIS builder reports",
    "version": "16.0.0.1.0",
    "author": "Open-Net Sàrl",
    "category": "Extra Tools",
    "website": "https://www.open-net.ch",
    "depends": ["mis_builder", "onsp_co2"],
    "data": [
        "views/mis_co2_account_move_line_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
