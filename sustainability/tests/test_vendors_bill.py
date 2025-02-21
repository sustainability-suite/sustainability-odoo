from datetime import datetime

from odoo import Command

from odoo.addons.sustainability.tests.common import CarbonCommon


class TestCarbonVendorsBill(CarbonCommon):
    def test_vendor_bill(self):
        # Check with the default values
        self.assertEqual(
            round(self.vendor_account_move_1.carbon_balance, 2), 10 * 100 * 10
        )
        self.check_sign(self.vendor_account_move_1)

    def test_vendor_action_post(self):
        for move in self.vendor_account_move:
            move.action_post()

    #### SETUP CLASS ####
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
                            price_unit=100.0,
                            tax_ids=False,
                        )
                    )
                ],
            )
        )
        cls.vendor_account_move |= cls.vendor_account_move_1
