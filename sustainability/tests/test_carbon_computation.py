from odoo import Command

from odoo.addons.sustainability.tests.common import CarbonCommon


class TestCarbonComputation(CarbonCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.carbon_factor_plastic_chair = cls.env["carbon.factor"].create(
            [
                {"name": "Plastic chair", "carbon_compute_method": "physical"},
            ]
        )

        carbon_factor_types = cls.env["carbon.factor.type"].create(
            [
                {"code": "Type 1", "name": "Type 1"},
                {"code": "Type 2", "name": "Type 2"},
            ]
        )

        carbon_factor_plastic_values = [
            {
                "factor_id": cls.carbon_factor_plastic_chair.id,
                "carbon_uom_id": cls.uom_unit.id,
                "date": "2025-01-01",
                "carbon_value": 20,
                "type_id": carbon_factor_types[0].id,
            },
            {
                "factor_id": cls.carbon_factor_plastic_chair.id,
                "carbon_uom_id": cls.uom_unit.id,
                "date": "2025-01-01",
                "carbon_value": 20,
                "type_id": carbon_factor_types[1].id,
            },
            {
                "factor_id": cls.carbon_factor_plastic_chair.id,
                "carbon_uom_id": cls.uom_unit.id,
                "date": "2024-01-01",
                "carbon_value": 10,
                "type_id": carbon_factor_types[0].id,
            },
            {
                "factor_id": cls.carbon_factor_plastic_chair.id,
                "carbon_uom_id": cls.uom_unit.id,
                "date": "2024-01-01",
                "carbon_value": 10,
                "type_id": carbon_factor_types[1].id,
            },
        ]
        cls.env["carbon.factor.value"].create(carbon_factor_plastic_values)

        cls.office_chair_product = cls.env["product.product"].create(
            {
                "name": "Office chair",
                "list_price": 70.00,
                "standard_price": 55.00,
                "type": "consu",
                "uom_id": cls.uom_unit.id,
                "carbon_in_factor_id": cls.carbon_factor_plastic_chair.id,
                "carbon_in_is_manual": True,
            }
        )

    def test_carbon_values_for_matching_invoice_date(self):
        """Verify correct carbon factor values are applied for invoices matching factor dates."""

        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "invoice_date": "2025-01-01",
                "currency_id": self.currency_usd.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.office_chair_product.id,
                            "quantity": 1.0,
                            "price_unit": 55.0,
                            "name": self.office_chair_product.name,
                        }
                    ),
                ],
            }
        )
        self.check_sign(invoice)

        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", invoice.id),
                ("factor_id", "=", self.carbon_factor_plastic_chair.id),
            ]
        )
        total_value = sum(origin.signed_value for origin in carbon_line_origins)

        self.assertEqual(
            total_value,
            40.0,
            "The carbon factor values matching the invoice date were not applied correctly.",
        )

    def test_carbon_values_for_earlier_invoice_date(self):
        """Verify correct carbon factor values are applied for invoices predating all factor values."""

        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "invoice_date": "2023-01-01",
                "currency_id": self.currency_usd.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.office_chair_product.id,
                            "quantity": 1.0,
                            "price_unit": 55.0,
                            "name": self.office_chair_product.name,
                        }
                    ),
                ],
            }
        )
        self.check_sign(invoice)

        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id", "=", invoice.id),
                ("factor_id", "=", self.carbon_factor_plastic_chair.id),
            ]
        )
        total_value = sum(origin.signed_value for origin in carbon_line_origins)

        self.assertEqual(
            total_value,
            20.0,
            "The computed total signed value for an invoice dated before "
            "the earliest carbon factor value is incorrect.",
        )
