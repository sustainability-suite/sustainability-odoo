from datetime import datetime

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

        # Carbon Factors
        (
            cls.carbon_factor_default_fallback,
            cls.carbon_factor_monetary,
            cls.carbon_factor_physical,
        ) = cls.env["carbon.factor"].create(
            [
                {
                    "name": "Global Emission Factor Fallback",
                    "carbon_compute_method": "monetary",
                },
                {"name": "Test monetary", "carbon_compute_method": "monetary"},
                {"name": "Test physical", "carbon_compute_method": "physical"},
            ]
        )

        cls.env["carbon.factor.value"].create(
            [
                {
                    "factor_id": cls.carbon_factor_default_fallback.id,
                    "carbon_monetary_currency_id": cls.currency_eur.id,
                    "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                    "carbon_value": 10,
                },
                {
                    "factor_id": cls.carbon_factor_monetary.id,
                    "carbon_monetary_currency_id": cls.currency_eur.id,
                    "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                    "carbon_value": 0.025,
                },
                {
                    "factor_id": cls.carbon_factor_physical.id,
                    "carbon_uom_id": cls.uom_hour.id,
                    "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                    "carbon_value": 0.022,
                },
            ]
        )

        # Currency Rates Reset (some will be recreated in the test_conversion)
        cls.env["res.currency.rate"].search([]).unlink()

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
