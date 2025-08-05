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

        cls.account_move = cls.env["account.move"].create(
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
            )
        )

    def test_account_with_distribution_lines(self):
        self.expense_account.write(
            {
                "carbon_in_is_manual": True,
                "carbon_in_factor_id": self.carbon_factor_a.id,
                "carbon_in_use_distribution": False,  # no effect yet
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
        carbon_origins = invoice_line.carbon_origin_ids

        self.assertEqual(len(carbon_origins), 1)
        self.assertEqual(carbon_origins.signed_value, 400.0)  # 4 * 100
        self.assertEqual(carbon_origins.distribution, 1.0)

        # Then activate distributions
        self.expense_account.carbon_in_use_distribution = True

        invoice_line.action_recompute_carbon()
        invoice_line.carbon_origin_ids._clean_orphan_lines()  # TODO: ABO check that pls!
        carbon_origins = invoice_line.carbon_origin_ids.sorted("signed_value")

        self.assertEqual(len(carbon_origins), 2)
        self.assertEqual(carbon_origins[0].signed_value, 300.0)  # 6 * 100 * 0.5
        self.assertEqual(carbon_origins[0].distribution, 0.5)
        self.assertEqual(carbon_origins[1].signed_value, 500.0)  # 10 * 100 * 0.5
        self.assertEqual(carbon_origins[1].distribution, 0.5)
