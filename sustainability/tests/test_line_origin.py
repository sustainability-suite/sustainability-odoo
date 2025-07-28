from datetime import datetime

from odoo import Command

from odoo.addons.sustainability.tests.common import CarbonCommon


class TestLineOrigin(CarbonCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_move = cls.env["account.move"]

        cls.carbon_factor_kilogram = cls.env["carbon.factor"].create(
            {
                "name": "Test Carbon Factor with kilogram UoM",
                "carbon_compute_method": "physical",
                "value_ids": [
                    Command.create(
                        {
                            "carbon_uom_id": cls.uom_kg.id,
                            "carbon_value": 2,
                            "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                        }
                    )
                ],
            }
        )

        cls.product_product_meter = cls.env["product.product"].create(
            {
                "name": "Product with meter UoM",
                "list_price": 10.00,
                "standard_price": 9.00,
                "uom_id": cls.uom_meter.id,
                "uom_po_id": cls.uom_meter.id,
                "weight": 3,
                "carbon_in_factor_id": cls.carbon_factor_kilogram.id,
                "carbon_in_is_manual": True,
                "carbon_out_factor_id": cls.carbon_factor_kilogram.id,
                "carbon_out_is_manual": True,
            }
        )

        cls.account_move_meter = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product_product_meter.id,
                            "quantity": 1,
                            "product_uom_id": cls.uom_km.id,
                        }
                    )
                ],
            }
        )
        cls.account_move |= cls.account_move_meter

    def test_account_move_check_sign(self):
        self.account_move.action_recompute_carbon()
        for account_move in self.account_move:
            self.check_sign(account_move)

    def test_line_origin_uom_conversion(self):
        self.account_move.action_recompute_carbon()
        for account_move in self.account_move:
            origin_child = account_move.carbon_origin_child_ids.filtered(
                lambda origin: origin.move_line_id.product_id
                == self.product_product_meter
            )
            self.assertEqual(origin_child.factor_id, self.carbon_factor_kilogram)
            self.assertEqual(origin_child.quantity, 3 * 1000)
            self.assertEqual(account_move.carbon_balance, 6 * 1000)
            self.assertEqual(origin_child.move_line_balance, 9 * 1000)
            self.assertEqual(origin_child.uom_id, self.uom_kg)

    def test_carbon_factor_compute_method_physical(self):
        quantity = self.carbon_factor_kilogram._get_physical_effective_quantity(
            factor_value=self.carbon_factor_kilogram.value_ids[0],
            quantity=1,
            from_uom_id=self.uom_km,
            product_id=self.product_product_meter,
        )
        self.assertEqual(quantity, 3 * 1000)
