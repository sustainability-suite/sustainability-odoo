import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-sustainability-suite-sustainability-odoo",
    description="Meta package for sustainability-suite-sustainability-odoo Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-sustainability>=16.0dev,<16.1dev',
        'odoo-addon-sustainability_account_asset_management>=16.0dev,<16.1dev',
        'odoo-addon-sustainability_employee_commuting>=16.0dev,<16.1dev',
        'odoo-addon-sustainability_hr_expense_report>=16.0dev,<16.1dev',
        'odoo-addon-sustainability_mis_builder>=16.0dev,<16.1dev',
        'odoo-addon-sustainability_purchase>=16.0dev,<16.1dev',
        'odoo-addon-sustainability_purchase_stock>=16.0dev,<16.1dev',
        'odoo-addon-sustainability_stock>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
