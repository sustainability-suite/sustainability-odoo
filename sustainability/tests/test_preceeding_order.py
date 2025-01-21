from odoo.fields import Command

from odoo.addons.sustainability.tests.common import CarbonCommon


class TestPreceedingOrder(CarbonCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "list_price": 50.00,
                "standard_price": 40.00,
                "uom_id": cls.uom_hour.id,
                "carbon_in_factor_id": cls.carbon_factor_physical.id,
                "carbon_in_is_manual": True,
            }
        )

    def test_carbon_on_invoice(self):
        """Verify carbon line origin values are correctly set for invoices with manually specified carbon data."""

        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "invoice_date": "2025-01-01",
                "currency_id": self.currency_usd.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 40.00,
                            "carbon_debt": 15.0,
                            "carbon_uncertainty_value": 0,
                            "carbon_is_locked": True,
                            "carbon_data_uncertainty_percentage": 0,
                            "carbon_origin_json": {
                                "mode": "manual",
                                "model_name": "account.move.line",
                            },
                        },
                    )
                ],
            }
        )

        carbon_line_origin = self.env["carbon.line.origin"].search(
            [
                ("factor_id", "=", None),
                ("move_id", "=", invoice.id),
                ("computation_level", "=", "Carbon on invoice"),
            ],
            limit=1,
        )

        expected_result = 15.0

        self.assertEqual(
            carbon_line_origin.signed_value,
            expected_result,
            f"Expected a value of {expected_result} for the carbon line origin.",
        )

    def test_carbon_on_product(self):
        """Verify carbon line origin values are correctly computed at the product level for invoices."""

        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "invoice_date": "2025-01-01",
                "currency_id": self.currency_usd.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 40.00,
                        },
                    )
                ],
            }
        )

        carbon_line_origin = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", invoice.id),
                ("computation_level", "=", "Product"),
            ],
            limit=1,
        )

        expected_result = 0.02

        self.assertEqual(
            round(carbon_line_origin.signed_value, 2),
            expected_result,
            f"Expected a value of {expected_result} for the product level carbon line origin.",
        )

    def test_carbon_on_product_category(self):
        """Verify carbon line origin values are correctly computed at the product category level for invoices."""

        product_category = self.env["product.category"].create(
            {
                "name": "Test Product Category",
                "carbon_in_is_manual": True,
                "carbon_in_factor_id": self.carbon_factor_physical.id,
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Product",
                "list_price": 50.00,
                "standard_price": 40.00,
                "uom_id": self.uom_hour.id,
                "categ_id": product_category.id,
            }
        )

        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "invoice_date": "2025-01-01",
                "currency_id": self.currency_usd.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "quantity": 1,
                            "price_unit": 40.00,
                        },
                    )
                ],
            }
        )
        invoice.action_recompute_carbon()

        carbon_line_origin = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", invoice.id),
                ("computation_level", "=", "Product category"),
            ],
            limit=1,
        )

        expected_result = 0.02

        self.assertEqual(
            round(carbon_line_origin.signed_value, 2),
            expected_result,
            f"Expected a value of {expected_result} for the product category level carbon line origin.",
        )

    def test_carbon_on_product_template(self):
        """Verify carbon line origin values are correctly computed at the product template level for invoices."""

        color_attribute = self.env["product.attribute"].create(
            {
                "name": "Color",
                "value_ids": [
                    Command.create({"name": "red", "sequence": 1}),
                ],
            }
        )
        (color_attribute_red,) = color_attribute.value_ids

        product_template = self.env["product.template"].create(
            {
                "name": "Test Product Template",
                "carbon_in_is_manual": True,
                "carbon_in_factor_id": self.carbon_factor_physical.id,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": color_attribute.id,
                            "value_ids": [
                                Command.set(
                                    [
                                        color_attribute_red.id,
                                    ]
                                )
                            ],
                        }
                    )
                ],
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Product",
                "list_price": 50.00,
                "standard_price": 40.00,
                "uom_id": self.uom_hour.id,
                "product_tmpl_id": product_template.id,
            }
        )

        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "invoice_date": "2025-01-01",
                "currency_id": self.currency_usd.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "quantity": 1,
                            "price_unit": 40.00,
                        },
                    )
                ],
            }
        )
        invoice.action_recompute_carbon()

        carbon_line_origin = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", invoice.id),
                ("computation_level", "=", "Product template"),
            ],
            limit=1,
        )

        expected_result = 0.02

        self.assertEqual(
            round(carbon_line_origin.signed_value, 2),
            expected_result,
            f"Expected a value of {expected_result} for the product template level carbon line origin.",
        )

    def test_carbon_on_account(self):
        """Verify carbon line origin values are correctly computed at the account level for invoices."""

        account = self.env["account.account"].create(
            {
                "name": "Account",
                "code": "REV1234",
                "account_type": "income",
                "company_id": self.env.company.id,
                "carbon_in_factor_id": self.carbon_factor_monetary.id,
                "carbon_in_is_manual": True,
            }
        )

        product = self.env["product.product"].create(
            {
                "name": "Product",
                "list_price": 50.00,
                "standard_price": 40.00,
                "uom_id": self.uom_hour.id,
            }
        )

        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "invoice_date": "2025-01-01",
                "currency_id": self.currency_usd.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "quantity": 1,
                            "price_unit": 40.00,
                            "account_id": account.id,
                        },
                    )
                ],
            }
        )

        carbon_line_origin = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", invoice.id),
                ("computation_level", "=", "Account"),
            ],
            limit=1,
        )

        expected_result = 0.95

        self.assertEqual(
            round(carbon_line_origin.signed_value, 2),
            expected_result,
            f"Expected a value of {expected_result} for the account level carbon line origin.",
        )

    def test_carbon_on_company_fallback(self):
        """Verify carbon line origin values are correctly computed at the company level for invoices."""

        product = self.env["product.product"].create(
            {
                "name": "Product",
                "list_price": 50.00,
                "standard_price": 40.00,
                "uom_id": self.uom_hour.id,
            }
        )

        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "invoice_date": "2025-01-01",
                "currency_id": self.currency_usd.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "quantity": 1,
                            "price_unit": 40.00,
                        },
                    )
                ],
            }
        )
        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", invoice.id),
                ("computation_level", "=", "Company fallback"),
            ],
        )
        total_value = sum(origin.signed_value for origin in carbon_line_origins)

        expected_result = 876.2

        self.assertEqual(
            round(total_value, 2),
            expected_result,
            f"Expected a total value of {expected_result} for the company level carbon line origin.",
        )
