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
        invoice.action_post()

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
            f"Expected a signed value of {expected_result} for the carbon line origin.",
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
                            "carbon_origin_json": {
                                "mode": "manual",
                                "model_name": "product.product",
                            },
                        },
                    )
                ],
            }
        )
        invoice.action_post()

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
            f"Expected a signed value of {expected_result} for the product level carbon line origin.",
        )
