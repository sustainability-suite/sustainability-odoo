from odoo.addons.sustainability.tests.common import CarbonCommon


class TestCarbonVendorsBill(CarbonCommon):
    def test_vendor_bill(self):
        # Check with the default values
        self.vendor_account_move_1.action_recompute_carbon()
        # self.assertEqual(round(self.vendor_account_move_1.carbon_balance, 2), 10*100*10) # TODO: Make sure this test pass as soon as possible

    def test_vendor_action_post(self):
        for move in self.vendor_account_move:
            move.action_post()
