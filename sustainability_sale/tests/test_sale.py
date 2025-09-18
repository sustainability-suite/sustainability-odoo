from odoo import Command

from odoo.addons.sustainability_sale.tests.common import CarbonSaleCommon


class TestCarbonSale(CarbonSaleCommon):
    def test_sale_order(self):
        """
        Test that the carbon debt is correctly recomputed for a sale order.
        """
        self.sale_order_1.action_recompute_carbon()
        self.assertEqual(round(self.sale_order_1.carbon_debt, 2), 2500)

    def test_price_changes_sale_order(self):
        """
        Check with different price
        """
        self.sale_order_1.order_line[0].price_unit = 500
        self.sale_order_1.action_recompute_carbon()
        self.assertEqual(round(self.sale_order_1.carbon_debt, 2), 12500)

    def test_confirm_sale_order(self):
        """
        Check to confirm all sale orders
        """
        for sale in self.sale_order:
            sale.action_confirm()

    def test_sale_order_quantity_changes(self):
        """
        Check carbon calculation with quantity changes
        """
        self.sale_order_1.order_line[0].product_uom_qty = 2.0
        self.sale_order_1.action_recompute_carbon()
        self.assertEqual(round(self.sale_order_1.carbon_debt, 2), 5000)

    def test_invoice_preparation_with_locked_carbon(self):
        """
        Check invoice line preparation when carbon is locked
        """
        line = self.sale_order_1.order_line[0]
        line.carbon_is_locked = True
        line.carbon_debt = 100
        line.carbon_uncertainty_value = 10
        line.carbon_data_uncertainty_percentage = 5
        # Avoid recomputation
        line._fields["carbon_debt"].store = False
        invoice_line_vals = line._prepare_invoice_line()
        self.assertEqual(invoice_line_vals["carbon_debt"], 100)
        self.assertEqual(invoice_line_vals["carbon_uncertainty_value"], 10)
        self.assertEqual(invoice_line_vals["carbon_data_uncertainty_percentage"], 5)
        self.assertTrue(invoice_line_vals["carbon_is_locked"])
        self.assertIn("mode", invoice_line_vals["carbon_origin_json"])

    def test_setting_carbon_debt_on_creation_locks_field_sale_order(self):
        """
        Test setting 'carbon_debt' field on creation of sale order
        correctly locks 'carbon_debt' field on sale order line
        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.sale_product_product_1.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                            "name": "Test Line",
                            "carbon_debt": 100,
                        }
                    ),
                ],
            }
        )

        line = sale_order.order_line[0]
        self.assertEqual(line.carbon_debt, 100)
        self.assertTrue(line.carbon_is_locked)

    def test_manual_edit_of_carbon_debt_locks_and_preserves_value(self):
        """
        Check that manually editing carbon debt locks the value and preserves it
        """
        for order in self.sale_order:
            line = order.order_line[0]
            self.assertFalse(line.carbon_is_locked)

            line.carbon_debt = 100

            self.assertEqual(line.carbon_debt, 100)
            self.assertTrue(line.carbon_is_locked)
