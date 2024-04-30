from odoo.addons.sustainability.tests.common import CarbonCommon


class TestCarbonUom(CarbonCommon):
    def test_10_uom(self):
        product_consulting_uom = self.env["product.product"].create(
            {
                "name": "Consulting",
                "type": "service",
                "categ_id": self.env.ref("product.product_category_all").id,
                "uom_id": self.uom_hour.id,
                "uom_po_id": self.uom_hour.id,
                "lst_price": 100.0,
                "standard_price": 50.0,
                "carbon_out_is_manual": True,
                "carbon_out_compute_method": "physical",
                "carbon_out_value": 2.5,
                "carbon_out_uom_id": self.uom_hour.id,
                "carbon_in_is_manual": True,
                "carbon_in_compute_method": "physical",
                "carbon_in_value": 1.5,
                "carbon_in_uom_id": self.uom_hour.id,
            }
        )

        invoice_out = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": self.env.ref("base.res_partner_2").id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Consulting",
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
            round(invoice_out.carbon_balance, 1),
            20.0,
            "Converted quantity for customer invoice does not correspond.",
        )

        invoice_in = self.env["account.move"].create(
            [
                {
                    "move_type": "in_invoice",
                    "partner_id": self.env.ref("base.res_partner_2").id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Consulting",
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
            round(invoice_in.carbon_balance, 1),
            12.0,
            "Converted quantity for vendor bill does not correspond.",
        )

    def test_20_currency(self):
        """Use EUR for carbon currency but USD for invoice"""
        product_consulting_currency = self.env["product.product"].create(
            {
                "name": "Consulting",
                "type": "service",
                "categ_id": self.env.ref("product.product_category_all").id,
                "lst_price": 10.0,
            }
        )

        invoice_out = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": self.env.ref("base.res_partner_2").id,
                    "invoice_date": "2023-01-01",
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Consulting",
                                "product_id": product_consulting_currency.id,
                                "quantity": 10.0,
                            },
                        ),
                    ],
                }
            ]
        )
        invoice_out.invoice_line_ids[:1].account_id.write(
            {
                "carbon_out_is_manual": True,
                "carbon_out_compute_method": "monetary",
                "carbon_out_value": 2,
                "carbon_out_monetary_currency_id": self.currency_eur.id,
            }
        )

        # Round to zero because of stupid rounding errors
        self.assertEqual(
            round(invoice_out.carbon_balance, 0),
            190.0,
            "Converted quantity for customer invoice does not correspond.",
        )
