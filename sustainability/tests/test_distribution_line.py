from datetime import datetime

from odoo import Command

from odoo.addons.sustainability.tests.common import CarbonCommon


class TestDistributionLine(CarbonCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        today = datetime.today().strftime("%Y-%m-%d")
        cls.carbon_factor_a, cls.carbon_factor_b, cls.carbon_factor_c = cls.env[
            "carbon.factor"
        ].create(
            [
                dict(
                    name="Test A",
                    carbon_compute_method="monetary",
                    value_ids=[
                        Command.create(
                            dict(
                                date=today,
                                carbon_monetary_currency_id=cls.currency_usd.id,
                                carbon_value=4,
                            )
                        )
                    ],
                ),
                dict(
                    name="Test B",
                    carbon_compute_method="monetary",
                    value_ids=[
                        Command.create(
                            dict(
                                date=today,
                                carbon_monetary_currency_id=cls.currency_usd.id,
                                carbon_value=6,
                            )
                        )
                    ],
                ),
                dict(
                    name="Test C",
                    carbon_compute_method="monetary",
                    value_ids=[
                        Command.create(
                            dict(
                                date=today,
                                carbon_monetary_currency_id=cls.currency_usd.id,
                                carbon_value=10,
                            )
                        )
                    ],
                ),
            ]
        )

        cls.carbon_distribution_template = cls.env[
            "carbon.distribution.template"
        ].create(
            dict(
                name="Distribution Test",
                carbon_distribution_line_ids=[
                    Command.create(
                        dict(
                            res_model="carbon.distribution.template",
                            carbon_type="template",
                            factor_id=cls.carbon_factor_b.id,
                            percentage=0.3,
                        )
                    ),
                    Command.create(
                        dict(
                            res_model="carbon.distribution.template",
                            carbon_type="template",
                            factor_id=cls.carbon_factor_c.id,
                            percentage=0.7,
                        )
                    ),
                ],
            )
        )

        cls.product_product = cls.env["product.product"].create(
            {
                "name": "Test product",
            }
        )

        cls.account_move, cls.account_move_product = cls.env["account.move"].create(
            [
                dict(
                    move_type="in_invoice",
                    partner_id=cls.partner.id,
                    invoice_date=today,
                    invoice_line_ids=[
                        Command.create(
                            dict(
                                name="Super test product",
                                account_id=cls.expense_account.id,
                                quantity=1.0,
                                price_unit=100.0,
                                tax_ids=False,
                            )
                        )
                    ],
                ),
                dict(
                    move_type="out_invoice",
                    partner_id=cls.partner.id,
                    invoice_date=today,
                    invoice_line_ids=[
                        Command.create(
                            dict(
                                product_id=cls.product_product.id,
                                account_id=cls.expense_account.id,
                                quantity=1.0,
                                price_unit=100.0,
                                tax_ids=False,
                            )
                        )
                    ],
                ),
            ]
        )

    def test_product_auto_carbon_distribution_in_from_factor(self):
        self.product_product.write(
            {
                "carbon_in_is_manual": True,
                "carbon_in_factor_id": self.carbon_factor_a.id,
            }
        )
        distribution = self.product_product.carbon_in_distribution_line_ids
        self.assertEqual(len(distribution), 1)
        self.assertEqual(distribution.factor_id, self.carbon_factor_a)
        self.assertEqual(distribution.percentage, 1.0)
        self.assertEqual(distribution.carbon_type, "in")
        self.assertEqual(distribution.res_model, "product.product")
        self.assertEqual(distribution.res_id, self.product_product.id)
        self.assertEqual(distribution.res_in_id, self.product_product.id)
        self.assertEqual(distribution.res_out_id, False)

    def test_product_auto_carbon_distribution_in_from_distribution_template(self):
        self.product_product.write(
            {
                "carbon_in_is_manual": True,
                "carbon_in_use_distribution": True,
                "carbon_in_distribution_template_id": self.carbon_distribution_template.id,
            }
        )
        distributions = self.product_product.carbon_in_distribution_line_ids.sorted(
            "percentage"
        )
        self.assertEqual(len(distributions), 2)
        self.assertEqual(distributions[0].factor_id, self.carbon_factor_b)
        self.assertEqual(distributions[0].percentage, 0.3)
        self.assertEqual(distributions[0].carbon_type, "in")
        self.assertEqual(distributions[0].res_model, "product.product")
        self.assertEqual(distributions[0].res_id, self.product_product.id)
        self.assertEqual(distributions[0].res_in_id, self.product_product.id)
        self.assertEqual(distributions[0].res_out_id, False)
        self.assertEqual(distributions[1].factor_id, self.carbon_factor_c)
        self.assertEqual(distributions[1].percentage, 0.7)
        self.assertEqual(distributions[1].carbon_type, "in")
        self.assertEqual(distributions[1].res_model, "product.product")
        self.assertEqual(distributions[1].res_id, self.product_product.id)
        self.assertEqual(distributions[1].res_in_id, self.product_product.id)
        self.assertEqual(distributions[1].res_out_id, False)

    def test_product_auto_carbon_distribution_out_from_factor(self):
        self.product_product.write(
            {
                "carbon_out_is_manual": True,
                "carbon_out_factor_id": self.carbon_factor_a.id,
            }
        )
        distribution = self.product_product.carbon_out_distribution_line_ids
        self.assertEqual(len(distribution), 1)
        self.assertEqual(distribution.factor_id, self.carbon_factor_a)
        self.assertEqual(distribution.percentage, 1.0)
        self.assertEqual(distribution.carbon_type, "out")
        self.assertEqual(distribution.res_model, "product.product")
        self.assertEqual(distribution.res_id, self.product_product.id)
        self.assertEqual(distribution.res_in_id, False)
        self.assertEqual(distribution.res_out_id, self.product_product.id)

    def test_product_auto_carbon_distribution_out_from_distribution_template(self):
        self.product_product.write(
            {
                "carbon_out_is_manual": True,
                "carbon_out_use_distribution": True,
                "carbon_out_distribution_template_id": self.carbon_distribution_template.id,
            }
        )
        distributions = self.product_product.carbon_out_distribution_line_ids.sorted(
            "percentage"
        )
        self.assertEqual(len(distributions), 2)
        self.assertEqual(distributions[0].factor_id, self.carbon_factor_b)
        self.assertEqual(distributions[0].percentage, 0.3)
        self.assertEqual(distributions[0].carbon_type, "out")
        self.assertEqual(distributions[0].res_model, "product.product")
        self.assertEqual(distributions[0].res_id, self.product_product.id)
        self.assertEqual(distributions[0].res_in_id, False)
        self.assertEqual(distributions[0].res_out_id, self.product_product.id)
        self.assertEqual(distributions[1].factor_id, self.carbon_factor_c)
        self.assertEqual(distributions[1].percentage, 0.7)
        self.assertEqual(distributions[1].carbon_type, "out")
        self.assertEqual(distributions[1].res_model, "product.product")
        self.assertEqual(distributions[1].res_id, self.product_product.id)
        self.assertEqual(distributions[1].res_in_id, False)
        self.assertEqual(distributions[1].res_out_id, self.product_product.id)

    def test_account_without_distribution(self):
        self.expense_account.write(
            {
                "carbon_in_is_manual": True,
                "carbon_in_factor_id": self.carbon_factor_a.id,
            }
        )
        self.check_sign(self.account_move)

        invoice_line = self.account_move.invoice_line_ids
        invoice_line.action_recompute_carbon()
        invoice_line.carbon_origin_ids._clean_orphan_lines()  # TODO: ABO check that pls!
        carbon_origins = invoice_line.carbon_origin_ids

        self.assertEqual(len(carbon_origins), 1)
        self.assertEqual(carbon_origins.signed_value, 400.0)  # 4 * 100
        self.assertEqual(carbon_origins.distribution, 1.0)

    def test_account_with_distribution_line(self):
        self.expense_account.write(
            {
                "carbon_in_is_manual": True,
                "carbon_in_use_distribution": True,
                "carbon_in_distribution_line_ids": [
                    Command.create(
                        dict(
                            res_model="account.account",
                            carbon_type="in",
                            factor_id=self.carbon_factor_b.id,
                            percentage=0.5,
                        )
                    ),
                    Command.create(
                        dict(
                            res_model="account.account",
                            carbon_type="in",
                            factor_id=self.carbon_factor_c.id,
                            percentage=0.5,
                        )
                    ),
                ],
            }
        )
        self.check_sign(self.account_move)

        invoice_line = self.account_move.invoice_line_ids
        invoice_line.action_recompute_carbon()
        invoice_line.carbon_origin_ids._clean_orphan_lines()  # TODO: ABO check that pls!
        carbon_origins = invoice_line.carbon_origin_ids.sorted("signed_value")

        self.assertEqual(len(carbon_origins), 2)
        self.assertEqual(carbon_origins[0].signed_value, 300.0)  # 6 * 100 * 0.5
        self.assertEqual(carbon_origins[0].distribution, 0.5)
        self.assertEqual(carbon_origins[1].signed_value, 500.0)  # 10 * 100 * 0.5
        self.assertEqual(carbon_origins[1].distribution, 0.5)

    def test_account_with_distribution_template(self):
        self.expense_account.write(
            {
                "carbon_in_is_manual": True,
                "carbon_in_use_distribution": True,
                "carbon_in_distribution_template_id": self.carbon_distribution_template.id,
            }
        )
        self.check_sign(self.account_move)

        invoice_line = self.account_move.invoice_line_ids
        invoice_line.action_recompute_carbon()
        invoice_line.carbon_origin_ids._clean_orphan_lines()  # TODO: ABO check that pls!
        carbon_origins = invoice_line.carbon_origin_ids.sorted("signed_value")

        self.assertEqual(len(carbon_origins), 2)
        self.assertEqual(carbon_origins[0].signed_value, 180.0)  # 6 * 100 * 0.3
        self.assertEqual(carbon_origins[0].distribution, 0.3)
        self.assertEqual(carbon_origins[1].signed_value, 700.0)  # 10 * 100 * 0.7
        self.assertEqual(carbon_origins[1].distribution, 0.7)

    def test_product_without_out_distribution(self):
        self.product_product.write(
            {
                "carbon_out_is_manual": True,
                "carbon_out_factor_id": self.carbon_factor_a.id,
            }
        )
        self.check_sign(self.account_move_product)

        invoice_line = self.account_move_product.invoice_line_ids
        invoice_line.action_recompute_carbon()
        invoice_line.carbon_origin_ids._clean_orphan_lines()  # TODO: ABO check that pls!
        carbon_origins = invoice_line.carbon_origin_ids

        self.assertEqual(len(carbon_origins), 1)
        self.assertEqual(carbon_origins.signed_value, -400.0)  # 4 * 100
        self.assertEqual(carbon_origins.distribution, 1.0)

    def test_product_with_out_distribution_line(self):
        self.product_product.write(
            {
                "carbon_out_is_manual": True,
                "carbon_out_use_distribution": True,
                "carbon_out_distribution_line_ids": [
                    Command.create(
                        dict(
                            res_model="product.product",
                            carbon_type="out",
                            factor_id=self.carbon_factor_b.id,
                            percentage=0.5,
                        )
                    ),
                    Command.create(
                        dict(
                            res_model="product.product",
                            carbon_type="out",
                            factor_id=self.carbon_factor_c.id,
                            percentage=0.5,
                        )
                    ),
                ],
            }
        )
        self.check_sign(self.account_move_product)

        invoice_line = self.account_move_product.invoice_line_ids
        invoice_line.action_recompute_carbon()
        invoice_line.carbon_origin_ids._clean_orphan_lines()  # TODO: ABO check that pls!
        carbon_origins = invoice_line.carbon_origin_ids.sorted("signed_value", True)

        self.assertEqual(len(carbon_origins), 2)
        self.assertEqual(carbon_origins[0].signed_value, -300.0)  # 6 * 100 * 0.5
        self.assertEqual(carbon_origins[0].distribution, 0.5)
        self.assertEqual(carbon_origins[1].signed_value, -500.0)  # 10 * 100 * 0.5
        self.assertEqual(carbon_origins[1].distribution, 0.5)

    def test_product_with_out_distribution_template(self):
        self.product_product.write(
            {
                "carbon_out_is_manual": True,
                "carbon_out_use_distribution": True,
                "carbon_out_distribution_template_id": self.carbon_distribution_template.id,
            }
        )
        self.check_sign(self.account_move_product)

        invoice_line = self.account_move_product.invoice_line_ids
        invoice_line.action_recompute_carbon()
        invoice_line.carbon_origin_ids._clean_orphan_lines()  # TODO: ABO check that pls!
        carbon_origins = invoice_line.carbon_origin_ids.sorted("signed_value", True)

        self.assertEqual(len(carbon_origins), 2)
        self.assertEqual(carbon_origins[0].signed_value, -180.0)  # 6 * 100 * 0.3
        self.assertEqual(carbon_origins[0].distribution, 0.3)
        self.assertEqual(carbon_origins[1].signed_value, -700.0)  # 10 * 100 * 0.7
        self.assertEqual(carbon_origins[1].distribution, 0.7)
