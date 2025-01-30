from odoo.addons.sustainability.tests.common import CarbonCommon


class TestCarbonPurchaseAction(CarbonCommon):
    """
    Here we are testing the actions of the carbon factor from the smart buttons. We only check the res_model, name, and domain of the actions. We've encountered problem in the past so we are testing it.
    """

    def test_contact_action(self):
        # Contact Action
        contact_action = self.carbon_factor_default_fallback.action_see_contact_ids()
        self.assertEqual(contact_action["res_model"], "res.partner")
        self.assertEqual(
            contact_action["name"],
            f"Contact {self.carbon_factor_default_fallback.name}",
        )
        self.assertEqual(
            contact_action["domain"],
            [
                (
                    "id",
                    "in",
                    self.carbon_factor_default_fallback._get_distribution_lines_res_ids(
                        "res.partner"
                    ),
                )
            ],
        )

    def test_supplierinfo_action(self):
        # Supplier Info Action
        supplierinfo_action = (
            self.carbon_factor_default_fallback.action_see_supplierinfo_ids()
        )
        self.assertEqual(supplierinfo_action["res_model"], "product.supplierinfo")
        self.assertEqual(
            supplierinfo_action["name"],
            f"Supplier Info {self.carbon_factor_default_fallback.name}",
        )
        self.assertEqual(
            supplierinfo_action["domain"],
            [
                (
                    "id",
                    "in",
                    self.carbon_factor_default_fallback._get_distribution_lines_res_ids(
                        "product.supplierinfo"
                    ),
                )
            ],
        )

    def test_child_action(self):
        # Child Action
        child_action = self.carbon_factor_default_fallback.action_see_child_ids()
        self.assertEqual(child_action["res_model"], "carbon.factor")
        self.assertEqual(
            child_action["domain"],
            [
                (
                    "id",
                    "in",
                    self.carbon_factor_default_fallback.child_ids.ids,
                )
            ],
        )

    def test_chart_of_account_action(self):
        # Chart of Account Action
        chart_of_account_action = (
            self.carbon_factor_default_fallback.action_see_chart_of_account_ids()
        )
        self.assertEqual(chart_of_account_action["res_model"], "account.account")
        self.assertEqual(
            chart_of_account_action["domain"],
            [
                (
                    "id",
                    "in",
                    self.carbon_factor_default_fallback._get_distribution_lines_res_ids(
                        "account.account"
                    ),
                )
            ],
        )

    def test_product_action(self):
        # Product Action
        product_action = self.carbon_factor_default_fallback.action_see_product_ids()
        self.assertEqual(product_action["res_model"], "product.template")
        self.assertEqual(
            product_action["domain"],
            [
                (
                    "id",
                    "in",
                    self.carbon_factor_default_fallback._get_distribution_lines_res_ids(
                        "product.template"
                    ),
                )
            ],
        )

    def test_product_categ_action(self):
        # Product Category Action
        product_categ_action = (
            self.carbon_factor_default_fallback.action_see_product_categ_ids()
        )
        self.assertEqual(product_categ_action["res_model"], "product.category")
        self.assertEqual(
            product_categ_action["domain"],
            [
                (
                    "id",
                    "in",
                    self.carbon_factor_default_fallback._get_distribution_lines_res_ids(
                        "product.category"
                    ),
                )
            ],
        )

    def test_account_move_action(self):
        # Account Move Action
        account_move_action = (
            self.carbon_factor_default_fallback.action_see_account_move_ids()
        )
        origins = self.env["carbon.line.origin"].search(
            [("factor_id", "in", self.carbon_factor_default_fallback.ids)]
        )
        self.assertEqual(account_move_action["res_model"], "account.move")
        self.assertEqual(
            account_move_action["domain"],
            [
                (
                    "id",
                    "in",
                    origins.move_id.ids,
                )
            ],
        )
