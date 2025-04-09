from odoo import Command

from odoo.addons.sustainability_purchase.tests.common import CarbonPurchaseCommon


class TestCarbonPurchase(CarbonPurchaseCommon):
    def test_partner_without_carbon_factor_on_supplierinfo_changes_purchase_order(self):
        """
        Check with a different partner without carbon factor on supplierinfo
        """
        self.purchase_purchase_order_5.partner_id = self.purchase_partner_3.id
        self.purchase_purchase_order_5.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_5.carbon_debt, 2), 2500)

    def test_partner_without_supplierinfo_purchase_order(self):
        """
        Check with a different partner without supplierinfo
        """
        self.purchase_purchase_order_6.partner_id = self.purchase_partner_4.id
        self.purchase_purchase_order_6.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_6.carbon_debt, 2), 2500)

    def test_purchase_order(self):
        """
        Check with the default values
        """
        self.purchase_purchase_order_1.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_1.carbon_debt, 2), 500)

    def test_partner_changes_purchase_order(self):
        """
        Check with a different partner
        """
        self.purchase_purchase_order_1.partner_id = self.purchase_partner_2.id
        self.purchase_purchase_order_1.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_1.carbon_debt, 2), 1000)

    def test_price_changes_purchase_order(self):
        """
        Check with different price
        """
        self.purchase_purchase_order_1.order_line[0].price_unit = 500
        self.purchase_purchase_order_1.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_1.carbon_debt, 2), 2500)

    def test_preceding_purchase_order_with_supplierinfo(self):
        """
        Check preceding purchase order
        """
        self.purchase_purchase_order_2.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_2.carbon_debt, 2), 1000)
        self.purchase_product_template_2.seller_ids = [
            Command.create(
                dict(
                    currency_id=self.currency_usd.id,
                    delay=0,
                    min_qty=1,
                    partner_id=self.purchase_partner_2.id,
                    price=100,
                    carbon_in_factor_id=self.purchase_carbon_factor_monetary_1.id,
                )
            ),
        ]
        self.purchase_purchase_order_2.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_2.carbon_debt, 2), 500)

    def test_preceding_purchase_order_without_supplierinfo(self):
        """
        Check preceding purchase order without supplierinfo
        """
        self.purchase_purchase_order_4.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_4.carbon_debt, 2), 2000)
        self.purchase_product_template_4.seller_ids = [
            Command.create(
                dict(
                    currency_id=self.currency_usd.id,
                    delay=0,
                    min_qty=1,
                    partner_id=self.purchase_partner_4.id,
                    price=100,
                )
            ),
        ]
        self.purchase_purchase_order_4.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_4.carbon_debt, 2), 2000)

    def test_purchase_order_recomputation(self):
        """
        Check recompute carbon with new supplierinfo
        """
        self.purchase_purchase_order_3.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_3.carbon_debt, 2), 1500)
        self.purchase_product_template_3.seller_ids = [
            Command.create(
                dict(
                    currency_id=self.currency_usd.id,
                    delay=0,
                    min_qty=1,
                    partner_id=self.purchase_partner_3.id,
                    price=100,
                    carbon_in_factor_id=self.purchase_carbon_factor_monetary_1.id,
                )
            ),
        ]
        self.purchase_purchase_order_3.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_3.carbon_debt, 2), 500)

        self.purchase_product_template_3.seller_ids[0].carbon_in_factor_id = False
        self.purchase_purchase_order_3.action_recompute_carbon()
        self.assertEqual(round(self.purchase_purchase_order_3.carbon_debt, 2), 1500)

    def test_validate_purchase_order(self):
        """
        Check to validate all purchase orders
        """
        for purchase in self.purchase_purchase_order:
            purchase.button_confirm()
