from datetime import datetime

from odoo.fields import Command

from odoo.addons.sustainability.tests.common import CarbonCommon


class TestCarbonUom(CarbonCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
                    "company_rate": 0.99,  # Fake rate in order to test the conversion
                    "currency_id": cls.currency_eur.id,
                },
            ]
        )

        (
            cls.carbon_factor_monetary,
            cls.carbon_factor_physical,
        ) = cls.env["carbon.factor"].create(
            [
                {"name": "Test monetary", "carbon_compute_method": "monetary"},
                {"name": "Test physical", "carbon_compute_method": "physical"},
            ]
        )

        carbon_values = [
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

    def test_10_uom(self):
        product_consulting_uom = self.env["product.product"].create(
            {
                "name": "Consulting uom test",
                "type": "service",
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
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product_consulting_uom.id,
                            "quantity": 1.0,
                            "product_uom_id": self.uom_day.id,
                        }
                    ),
                ],
            }
        )
        self.check_sign(invoice_out)
        self.assertEqual(
            round(invoice_out.carbon_balance, 2),
            -0.18,
            "Converted quantity for customer invoice does not correspond.",
        )

        invoice_in = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product_consulting_uom.id,
                            "quantity": 1.0,
                            "product_uom_id": self.uom_day.id,
                        }
                    ),
                ],
            }
        )
        self.check_sign(invoice_in)
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
                "lst_price": 10.0,
                "carbon_out_is_manual": True,
                "carbon_out_factor_id": self.carbon_factor_monetary.id,
                "currency_id": self.currency_usd.id,
            }
        )

        invoice_out = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": "2023-01-01",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product_consulting_currency.id,
                            "quantity": 10.0,
                        }
                    ),
                ],
            }
        )
        self.check_sign(invoice_out)

        self.assertEqual(
            round(invoice_out.carbon_balance, 2),
            -2.48,
            "Converted quantity for customer invoice does not correspond.",
        )
