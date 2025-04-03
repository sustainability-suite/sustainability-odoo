from datetime import datetime

from odoo import Command
from odoo.tests import tagged

from odoo.addons.sustainability.tests.common import CarbonCommon


@tagged("ef_by_weight")
class TestEFByWeight(CarbonCommon):
    def test_ef_by_weight(self):
        """
        Verify that an invoice line with a product that has a carbon factor with
        the unit of measure as kg correctly uses weight calculation.
        """

        self.check_sign(self.ef_by_weight_invoice)
        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", self.ef_by_weight_invoice.id),
                ("factor_id", "=", self.ef_by_weight_carbon_factor.id),
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

        self.ef_by_weight_invoice.write(
            {
                "invoice_line_ids": [
                    (
                        1,
                        self.ef_by_weight_invoice.invoice_line_ids[0].id,
                        {"quantity": 2.0},
                    )
                ]
            }
        )
        self.check_sign(self.ef_by_weight_invoice)

        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", self.ef_by_weight_invoice.id),
                ("factor_id", "=", self.ef_by_weight_carbon_factor.id),
            ]
        )
        total_value = sum(origin.signed_value for origin in carbon_line_origins)

        self.assertEqual(
            total_value,
            20.0,
            "The carbon factor was not correctly applied for quantity 2.",
        )

    def test_ef_by_weight_uom_change(self):
        """
        Verify that an invoice line with a product that has a carbon factor with
        the unit of measure changed to kilometers (km) correctly applies the weight calculation.
        """

        self.ef_by_weight_product_product_1.write(
            {"uom_id": self.uom_meter.id, "categ_id": self.uom_meter.category_id.id}
        )

        self.ef_by_weight_invoice.write(
            {
                "invoice_line_ids": [
                    (
                        1,
                        self.ef_by_weight_invoice.invoice_line_ids[0].id,
                        {
                            "product_uom_id": self.uom_km.id,
                        },
                    )
                ],
            }
        )
        self.check_sign(self.ef_by_weight_invoice)

        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", self.ef_by_weight_invoice.id),
                ("factor_id", "=", self.ef_by_weight_carbon_factor.id),
            ]
        )
        total_value = sum(origin.signed_value for origin in carbon_line_origins)

        self.assertEqual(
            total_value,
            10000.0,
            "The carbon factor was not correctly applied.",
        )

    def test_ef_by_weight_conversion(self):
        """
        Verify that an invoice line with a product that has a carbon factor using grams
        correctly converts and applies the weight calculation.
        """

        uom_gram = self.env.ref("uom.product_uom_gram")
        self.ef_by_weight_carbon_factor.value_ids[0].write(
            {"carbon_uom_id": uom_gram.id}
        )

        self.ef_by_weight_invoice.action_recompute_carbon()
        self.check_sign(self.ef_by_weight_invoice)

        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", self.ef_by_weight_invoice.id),
                ("factor_id", "=", self.ef_by_weight_carbon_factor.id),
            ]
        )
        total_value = sum(origin.signed_value for origin in carbon_line_origins)

        self.assertEqual(
            total_value,
            10000.0,
            "The carbon factor was not correctly converted from grams.",
        )

    #### SETUP CLASS ####
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_kgm = cls.env.ref("uom.product_uom_kgm")
        cls.uom_km = cls.env.ref("uom.product_uom_km")
        cls.uom_meter = cls.env.ref("uom.product_uom_meter")

        cls.ef_by_weight_carbon_factor = cls.env["carbon.factor"].create(
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

        cls.ef_by_weight_product_category_1 = cls.env["product.category"].create(
            dict(
                name="EF By Weight Product Category 1",
            )
        )
        cls.ef_by_weight_product_template_1 = cls.env["product.template"].create(
            dict(
                name="EF By Weight Product 1",
                categ_id=cls.ef_by_weight_product_category_1.id,
                list_price=100.0,
                carbon_in_factor_id=cls.ef_by_weight_carbon_factor.id,
            )
        )
        cls.ef_by_weight_product_product_1 = cls.env["product.product"].search(
            [("product_tmpl_id", "=", cls.ef_by_weight_product_template_1.id)], limit=1
        )

        cls.ef_by_weight_product_product_1.write(
            dict(
                carbon_in_is_manual=True,
                carbon_in_factor_id=cls.ef_by_weight_carbon_factor.id,
                weight=1,
            )
        )

        cls.ef_by_weight_invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "invoice_date": "2025-01-01",
                "currency_id": cls.currency_usd.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.ef_by_weight_product_product_1.id,
                            "quantity": 1.0,
                            "price_unit": 10.0,
                        }
                    ),
                ],
            }
        )
