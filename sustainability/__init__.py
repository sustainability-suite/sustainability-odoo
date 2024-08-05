# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import models
from . import tests


from datetime import date


def post_init_hook(env):
    """Create `carbon.line.origin` records if demo data"""
    if env.ref("base.user_demo", raise_if_not_found=False):
        vendor_bill = env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": env.ref("base.res_partner_12").id,
                "invoice_date": date.today(),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": env.ref("product.consu_delivery_02").id,
                            "quantity": 1,
                            "price_unit": 4500,
                            "account_id": env.ref("account.1_expense").id,
                            "carbon_debt": 450,
                            "carbon_uncertainty_value": 0,
                            "carbon_is_locked": True,
                            "carbon_data_uncertainty_percentage": 0,
                            "carbon_origin_json": {
                                "mode": "manual",
                                "details": {
                                    "uid": env.uid,
                                    "username": env.user.name,
                                },
                                "model_name": "account.move.line",
                            },
                        },
                    ),
                ],
            }
        )
        vendor_bill.action_post()

        move_types = ["out_invoice", "in_invoice", "out_refund", "in_refund"]
        moves = env["account.move"].search([("move_type", "in", move_types)])
        for move in moves:
            move.action_recompute_carbon()
