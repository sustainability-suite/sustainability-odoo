from datetime import datetime

from odoo import Command
from odoo.tests import TransactionCase


class CarbonCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Disable tracking test suite
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)

        # UoMs and Currencies
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.currency_usd = cls.env.ref("base.USD")

        # Global Carbon Factor
        cls.carbon_factor_default_fallback = cls.env["carbon.factor"].create(
            {
                "name": "Global Emission Factor Fallback",
                "carbon_compute_method": "monetary",
            }
        )
        cls.env["carbon.factor.value"].create(
            {
                "factor_id": cls.carbon_factor_default_fallback.id,
                "carbon_monetary_currency_id": cls.currency_eur.id,
                "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                "carbon_value": 10,
            }
        )
        # Currency Rates
        cls.env["res.currency.rate"].search([]).unlink()
        cls.env["res.currency.rate"].create(
            [
                {
                    "name": "2010-01-01",
                    "company_rate": 1,
                    "inverse_company_rate": 1,
                    "rate": 1,
                    "currency_id": cls.currency_usd.id,
                },
                {
                    "name": "2023-01-01",
                    "company_rate": 0.952380952381,
                    "currency_id": cls.currency_eur.id,
                },
            ]
        )

        # Company Setup
        cls.env.company.write(
            {
                "currency_id": cls.currency_usd.id,
                "carbon_in_factor_id": cls.carbon_factor_default_fallback.id,
                "carbon_out_factor_id": cls.carbon_factor_default_fallback.id,
            }
        )

        # Partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test.partner@example.com",
                "phone": "+123456789",
                "street": "123 Test Street",
                "city": "Test City",
                "country_id": cls.env.ref("base.us").id,
            }
        )

        # Account
        cls.revenue_account = cls.env["account.account"].create(
            {
                "name": "Test Revenue Account",
                "code": "REV1234",
                "account_type": "income",
                "company_id": cls.env.company.id,
            }
        )

        # User
        cls.user = cls.user_model.create(
            {
                "name": "Test User",
                "login": "test_user",
                "email": "test.user@example.com",
                "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
            }
        )
        cls.setUpClassVendor()

    @classmethod
    def setUpClassVendor(cls):
        # Vendor Bills Related
        # Vendor Carbon Factors
        cls.vendor_carbon_factor_vendor_1 = cls.env["carbon.factor"].create(
            dict(
                name="Vendor Carbon Factor 1 (VENDOR)",
                carbon_compute_method="monetary",
                value_ids=[
                    Command.create(
                        dict(
                            date=datetime.today().strftime("%Y-%m-%d %H:%M"),
                            carbon_monetary_currency_id=cls.currency_usd.id,
                            carbon_value=5,
                        )
                    )
                ],
            )
        )
        cls.vendor_carbon_factor_product_1 = cls.env["carbon.factor"].create(
            dict(
                name="Vendor Carbon Factor 1 (PRODUCT)",
                carbon_compute_method="monetary",
                value_ids=[
                    Command.create(
                        dict(
                            date=datetime.today().strftime("%Y-%m-%d %H:%M"),
                            carbon_monetary_currency_id=cls.currency_usd.id,
                            carbon_value=10,
                        )
                    )
                ],
            )
        )
        # Vendor Partner
        cls.vendor_partner_1 = cls.env["res.partner"].create(
            dict(
                name="Vendor Partner 1",
                email="vendor@email.com",
                phone="+123456789",
                street="123 Vendor Street",
                city="Vendor City",
                country_id=cls.env.ref("base.us").id,
                carbon_in_factor_id=cls.vendor_carbon_factor_vendor_1.id,
            )
        )

        # Vendor Product Category
        cls.vendor_product_category_1 = cls.env["product.category"].create(
            dict(
                name="Vendor Product Category 1",
            )
        )
        # Vendor Product Template
        cls.vendor_product_template_1 = cls.env["product.template"].create(
            dict(
                name="Vendor Product 1",
                categ_id=cls.vendor_product_category_1.id,
                list_price=100.0,
                carbon_in_factor_id=cls.vendor_carbon_factor_product_1.id,
                seller_ids=[
                    Command.create(
                        dict(
                            currency_id=cls.currency_usd.id,
                            delay=0,
                            min_qty=1,
                            partner_id=cls.vendor_partner_1.id,
                            price=100,
                        )
                    )
                ],
            )
        )
        # Vendor Product Product
        cls.vendor_product_product_1 = cls.env["product.product"].search(
            [("product_tmpl_id", "=", cls.vendor_product_template_1.id)], limit=1
        )
        # Vendor Account Move
        cls.vendor_account_move = cls.env["account.move"]
        cls.vendor_account_move_1 = cls.env["account.move"].create(
            dict(
                move_type="in_invoice",
                partner_id=cls.vendor_partner_1.id,
                invoice_date=datetime.today().strftime("%Y-%m-%d"),
                invoice_line_ids=[
                    Command.create(
                        dict(
                            product_id=cls.vendor_product_product_1.id,
                            quantity=10.0,
                        )
                    )
                ],
            )
        )
        cls.vendor_account_move |= cls.vendor_account_move_1
