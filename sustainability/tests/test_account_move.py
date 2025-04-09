from odoo import Command, fields

from odoo.addons.sustainability.tests.common import CarbonCommon

MOVE_TYPE_MAPPING = {
    "entry": "in",
    "out_invoice": "out",
    "out_refund": "out",
    "in_invoice": "in",
    "in_refund": "in",
    "out_receipt": "out",
    "in_receipt": "in",
}


class TestAccountMove(CarbonCommon):
    def test_move_type(self):
        for move in self.account_move:
            self.assertEqual(
                move.invoice_line_ids[0]._get_carbon_move_type(),
                MOVE_TYPE_MAPPING[move.move_type],
            )

    def test_post_account_move(self):
        today_date = fields.Date.today()
        for move in self.account_move:
            move.date = today_date
            move.invoice_date = today_date
            move.action_post()

            self.assertEqual(move.state, "posted")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_move = cls.env["account.move"]

        cls.account_expense = cls.env["account.account"].search(
            [("account_type", "=", "expense")], limit=1
        )

        # Entry Move Type
        cls.account_move_internal = cls.env["account.move"].create(
            dict(
                move_type="entry",
                invoice_line_ids=[
                    Command.create(
                        {
                            "account_id": cls.account_expense.id,
                            "quantity": 1.0,
                            "price_unit": 55.0,
                            "name": "Test Line",
                        }
                    ),
                ],
            )
        )
        cls.account_move |= cls.account_move_internal

        # Out Move Type
        cls.account_move_out = cls.env["account.move"].create(
            dict(
                move_type="out_invoice",
                partner_id=cls.partner.id,
                invoice_line_ids=[
                    Command.create(
                        {
                            "account_id": cls.account_expense.id,
                            "quantity": 1.0,
                            "price_unit": 55.0,
                            "name": "Test Line",
                        }
                    ),
                ],
            )
        )
        cls.account_move |= cls.account_move_out

        # Out Refund Move Type
        cls.account_move_out_refund = cls.env["account.move"].create(
            dict(
                move_type="out_refund",
                partner_id=cls.partner.id,
                invoice_line_ids=[
                    Command.create(
                        {
                            "account_id": cls.account_expense.id,
                            "quantity": 1.0,
                            "price_unit": 55.0,
                            "name": "Test Line",
                        }
                    ),
                ],
            )
        )
        cls.account_move |= cls.account_move_out_refund

        # In Move Type
        cls.account_move_in = cls.env["account.move"].create(
            dict(
                move_type="in_invoice",
                partner_id=cls.partner.id,
                invoice_line_ids=[
                    Command.create(
                        {
                            "account_id": cls.account_expense.id,
                            "quantity": 1.0,
                            "price_unit": 55.0,
                            "name": "Test Line",
                        }
                    ),
                ],
            )
        )
        cls.account_move |= cls.account_move_in

        # In Refund Move Type
        cls.account_move_in_refund = cls.env["account.move"].create(
            dict(
                move_type="in_refund",
                partner_id=cls.partner.id,
                invoice_line_ids=[
                    Command.create(
                        {
                            "account_id": cls.account_expense.id,
                            "quantity": 1.0,
                            "price_unit": 55.0,
                            "name": "Test Line",
                        }
                    ),
                ],
            )
        )
        cls.account_move |= cls.account_move_in_refund

        # Out Receipt Move Type
        cls.account_move_out_receipt = cls.env["account.move"].create(
            dict(
                move_type="out_receipt",
                partner_id=cls.partner.id,
                invoice_line_ids=[
                    Command.create(
                        {
                            "account_id": cls.account_expense.id,
                            "quantity": 1.0,
                            "price_unit": 55.0,
                            "name": "Test Line",
                        }
                    ),
                ],
            )
        )
        cls.account_move |= cls.account_move_out_receipt

        # In Receipt Move Type
        cls.account_move_in_receipt = cls.env["account.move"].create(
            dict(
                move_type="in_receipt",
                partner_id=cls.partner.id,
                invoice_line_ids=[
                    Command.create(
                        {
                            "account_id": cls.account_expense.id,
                            "quantity": 1.0,
                            "price_unit": 55.0,
                            "name": "Test Line",
                        }
                    ),
                ],
            )
        )
        cls.account_move |= cls.account_move_in_receipt
