# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License OPL-1 or later (https://www.odoo.com/documentation/14.0/legal/licenses.html#odoo-apps).

{
    "name": "Open Net Productivity: CO2 MIS Builder",
    "summary": "Provide CO2 accounting lines data for MIS builder reports",
    "version": "1.0",
    "author": "Open-Net Sàrl",
    "category": "Extra Tools",
    "website": "www.open-net.ch",
    "depends": ["mis_builder", "ons_productivity_co2_account"],
    "data": [
        "views/mis_co2_account_move_line_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "license": "OPL-1",
}
