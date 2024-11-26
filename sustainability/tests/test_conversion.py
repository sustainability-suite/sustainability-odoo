from odoo.addons.sustainability.tests.common import CarbonCommon


class TestCarbonUom(CarbonCommon):
    def test_10_uom(self):
        product_consulting_uom = self.env["product.product"].create(
            {
                "name": "Consulting uom test",
                "type": "service",
                "categ_id": self.product_category.id,
                "uom_id": self.uom_hour.id,
                "uom_po_id": self.uom_hour.id,
                "lst_price": 100.0,
                "standard_price": 50.0,
                "carbon_out_is_manual": True,
                "carbon_out_factor_id": self.carbon_factor_physical.id,
                "carbon_in_is_manual": True,
                "carbon_in_factor_id": self.carbon_factor_physical.id,
            }
        )

        invoice_out = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": self.partner.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": product_consulting_uom.id,
                                "quantity": 1.0,
                                "product_uom_id": self.uom_day.id,
                            },
                        ),
                    ],
                }
            ]
        )
        self.assertEqual(
            round(invoice_out.carbon_balance, 2),
            -0.18,
            "Converted quantity for customer invoice does not correspond.",
        )

        invoice_in = self.env["account.move"].create(
            [
                {
                    "move_type": "in_invoice",
                    "partner_id": self.partner.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": product_consulting_uom.id,
                                "quantity": 1.0,
                                "product_uom_id": self.uom_day.id,
                            },
                        ),
                    ],
                }
            ]
        )
        self.assertEqual(
            round(invoice_in.carbon_balance, 2),
            0.18,
            "Converted quantity for vendor bill does not correspond.",
        )

    def test_20_currency(self):
        """Use EUR for carbon currency but USD for invoice"""
        product_consulting_currency = self.env["product.product"].create(
            {
                "name": "Consulting currency test",
                "type": "service",
                "categ_id": self.product_category.id,
                "lst_price": 10.0,
                "carbon_out_is_manual": True,
                "carbon_out_factor_id": self.carbon_factor_monetary.id,
                "currency_id": self.env.ref("base.USD"),
            }
        )

        invoice_out = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": self.partner.id,
                    "invoice_date": "2023-01-01",
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": product_consulting_currency.id,
                                "quantity": 10.0,
                            },
                        ),
                    ],
                }
            ]
        )

        self.assertEqual(
            round(invoice_out.carbon_balance, 2),
            -2.38,
            "Converted quantity for customer invoice does not correspond.",
        )
