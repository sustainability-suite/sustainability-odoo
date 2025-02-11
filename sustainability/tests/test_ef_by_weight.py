from datetime import datetime

from odoo import Command
from odoo.tests import tagged

from odoo.addons.sustainability.tests.common import CarbonCommon


@tagged("ef_by_weight")
class TestEFByWeight(CarbonCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_kgm = cls.env.ref("uom.product_uom_kgm")

        cls.carbon_factor = cls.env["carbon.factor"].create(
            dict(
                name="Test",
                carbon_compute_method="physical",
                value_ids=[
                    Command.create(
                        dict(
                            date=datetime.today().strftime("%Y-%m-%d %H:%M"),
                            carbon_uom_id=cls.uom_kgm.id,
                            carbon_value=10,
                        )
                    )
                ],
            )
        )

        cls.vendor_product_product_1.update(
            dict(
                carbon_in_is_manual=True,
                carbon_in_factor_id=cls.carbon_factor.id,
                weight=1,
            )
        )

        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "invoice_date": "2025-01-01",
                "currency_id": cls.currency_usd.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.vendor_product_product_1.id,
                            "quantity": 1.0,
                            "price_unit": 10.0,
                        }
                    ),
                ],
            }
        )

    def test_ef_by_weight(self):
        """
        Verify that an invoice line with a product that has a carbon factor with
        the unit of measure as kg correctly uses weight calculation.
        """

        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", self.invoice.id),
                ("factor_id", "=", self.carbon_factor.id),
            ]
        )
        total_value = sum(origin.signed_value for origin in carbon_line_origins)

        self.assertEqual(
            total_value,
            10.0,
            "The carbon factor was not correctly applied.",
        )

    def test_ef_by_weight_qty(self):
        """
        Verify that an invoice line with a product that has a carbon factor with
        the unit of measure as kg correctly uses weight calculation for a quantity of 2.
        """

        self.invoice.write(
            {
                "invoice_line_ids": [
                    (1, self.invoice.invoice_line_ids[0].id, {"quantity": 2.0})
                ]
            }
        )

        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", self.invoice.id),
                ("factor_id", "=", self.carbon_factor.id),
            ]
        )
        total_value = sum(origin.signed_value for origin in carbon_line_origins)

        self.assertEqual(
            total_value,
            20.0,
            "The carbon factor was not correctly applied for quantity 2.",
        )

    def test_ef_by_weight_conversion(self):
        """
        Verify that an invoice line with a product that has a carbon factor using grams
        correctly converts and applies the weight calculation.
        """

        uom_gram = self.env.ref("uom.product_uom_gram")
        self.carbon_factor.value_ids[0].write({"carbon_uom_id": uom_gram.id})

        self.invoice.action_recompute_carbon()

        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", self.invoice.id),
                ("factor_id", "=", self.carbon_factor.id),
            ]
        )
        total_value = sum(origin.signed_value for origin in carbon_line_origins)

        self.assertEqual(
            total_value,
            10000.0,
            "The carbon factor was not correctly converted from grams.",
        )
