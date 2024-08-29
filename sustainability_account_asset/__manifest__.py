{
    "name": "Open Net Productivity: Carbon for assets ",
    "summary": "Glue module to make Sustainability module compatible with account_asset from Odoo",
    "version": "17.0.1.0.0",
    "author": "Open Net Sàrl, Julien Guenat, Adam Bonnet, Jacopo Bacci",
    "maintainers": ["jguenat", "bonnetadam", "jacopobacci"],
    "development_status": "Production/Stable",
    "category": "Accounting/Sustainability",
    "website": "https://www.open-net.ch",
    "depends": ["account_asset", "sustainability"],
    "data": [
        "views/account_asset.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "AGPL-3",
}
