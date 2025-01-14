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

        # Carbon Factors and Values
        cls.carbon_factor_default_fallback = cls.env["carbon.factor"].create(
            {
                "name": "Global Emission Factor Fallback",
                "carbon_compute_method": "monetary",
            }
        )
        (
            cls.carbon_factor_monetary,
            cls.carbon_factor_physical,
            cls.carbon_factor_plastic_chair,
        ) = cls.env["carbon.factor"].create(
            [
                {"name": "Test monetary", "carbon_compute_method": "monetary"},
                {"name": "Test physical", "carbon_compute_method": "physical"},
                {"name": "Plastic chair", "carbon_compute_method": "physical"},
            ]
        )

        carbon_values = [
            {
                "factor_id": cls.carbon_factor_default_fallback.id,
                "carbon_monetary_currency_id": cls.currency_eur.id,
                "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                "carbon_value": 10.0,
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
        cls.env["carbon.factor.value"].create(carbon_values)

        carbon_factor_types = cls.env["carbon.factor.type"].create(
            [
                {"code": "Type 1", "name": "Type 1"},
                {"code": "Type 2", "name": "Type 2"},
                {"code": "Type 3", "name": "Type 3"},
            ]
        )

        carbon_factor_plastic_values = [
            {
                "factor_id": cls.carbon_factor_plastic_chair.id,
                "carbon_uom_id": cls.uom_unit.id,
                "date": "2022-01-01",
                "carbon_value": 10,
                "type_id": carbon_factor_types[0].id,
            },
            {
                "factor_id": cls.carbon_factor_plastic_chair.id,
                "carbon_uom_id": cls.uom_unit.id,
                "date": "2022-01-01",
                "carbon_value": 10,
                "type_id": carbon_factor_types[1].id,
            },
            {
                "factor_id": cls.carbon_factor_plastic_chair.id,
                "carbon_uom_id": cls.uom_unit.id,
                "date": "2022-01-01",
                "carbon_value": 20,
                "type_id": carbon_factor_types[2].id,
            },
        ]
        cls.env["carbon.factor.value"].create(carbon_factor_plastic_values)

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

        # Product Category
        cls.product_category = cls.env["product.category"].create(
            {
                "name": "Test Product Category",
                "carbon_in_is_manual": True,
                "carbon_in_factor_id": cls.carbon_factor_monetary.id,
            }
        )

        # Office Chair Product
        cls.office_char_product = cls.env["product.product"].create(
            {
                "name": "Office chair",
                "list_price": 150.00,
                "standard_price": 100.00,
                "detailed_type": "consu",
                "categ_id": cls.product_category.id,
                "uom_id": cls.uom_unit.id,
                "carbon_in_factor_id": cls.carbon_factor_plastic_chair.id,
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

        # Invoice Creation
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "date": datetime.today().strftime("%Y-%m-%d"),
                "currency_id": cls.currency_eur.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.office_char_product.id,
                            "quantity": 1.0,
                            "price_unit": cls.office_char_product.list_price,
                            "name": cls.office_char_product.name,
                            "account_id": cls.revenue_account.id,
                            "product_uom_id": cls.office_char_product.uom_id.id,
                        },
                    )
                ],
            }
        )
