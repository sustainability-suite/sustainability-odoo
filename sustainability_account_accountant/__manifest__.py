{
    "name": "Sustainability Accounting (enterprise)",
    "category": "Accounting/Sustainability",
    "version": "16.0.1.0.0",
    "installable": True,
    "auto_install": True,
    "application": False,
    "license": "LGPL-3",
    "author": "MCO2, Open Net Sàrl",
    "maintainers": ["jguenat", "bonnetadam", "jacopobacci"],
    "development_status": "Production/Stable",
    "website": "https://github.com/sustainability-suite/sustainability-odoo",
    "depends": ["sustainability", "account_accountant"],
    "assets": {
        "web.assets_backend": [],
    },
    "data": [
        "wizards/account_change_lock_date.xml",
    ],
    "qweb": [],
}
