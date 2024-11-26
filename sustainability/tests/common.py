from datetime import datetime

from odoo.tests import TransactionCase


class CarbonCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # UoMs and Currencies
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.currency_usd = cls.env.ref("base.USD")

        # Carbon Factors
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
                "carbon_value": 10.000000,
            }
        )
        cls.carbon_factor_monetary = cls.env["carbon.factor"].create(
            {
                "name": "Test monetary",
                "carbon_compute_method": "monetary",
            }
        )
        cls.env["carbon.factor.value"].create(
            {
                "factor_id": cls.carbon_factor_monetary.id,
                "carbon_monetary_currency_id": cls.currency_eur.id,
                "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                "carbon_value": 0.025000,
            }
        )
        cls.carbon_factor_physical = cls.env["carbon.factor"].create(
            {
                "name": "Test physical",
                "carbon_compute_method": "physical",
            }
        )
        cls.env["carbon.factor.value"].create(
            {
                "factor_id": cls.carbon_factor_physical.id,
                "carbon_uom_id": cls.uom_hour.id,
                "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                "carbon_value": 0.022000,
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

        # Company
        cls.env.company.write(
            {
                "currency_id": cls.currency_usd.id,
                "carbon_in_factor_id": cls.carbon_factor_default_fallback.id,
                "carbon_out_factor_id": cls.carbon_factor_default_fallback.id,
            }
        )

        # Product Category
        cls.product_category = cls.env["product.category"].create(
            {
                "name": "Test Product Category",
                "carbon_in_is_manual": True,
                "carbon_in_factor_id": cls.carbon_factor_monetary.id,
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

        # User
        cls.user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "email": "test.user@example.com",
                "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
            }
        )
