from odoo import Command
from odoo.tests import Form, TransactionCase


class CarbonCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)

        currency_usd = cls.env.ref("base.USD")

        moves = cls.env["account.move"].search([("state", "=", "posted")])
        moves.button_draft()
        moves.unlink()

        (
            carbon_freight_product_upstream,
            carbon_freight_product_downstream,
        ) = cls.env["product.product"].create(
            [
                {
                    "name": "Upstream Product",
                    "type": "consu",
                    "is_storable": True,
                },
                {
                    "name": "Downstream Product",
                    "type": "consu",
                    "is_storable": True,
                },
            ]
        )

        carbon_journal = cls.env["account.journal"].create(
            {
                "name": "Carbon",
                "code": "CO2TEST",
                "type": "purchase",
                "company_id": cls.env.company.id,
                "currency_id": currency_usd.id,
            }
        )
        carbon_account = cls.env["account.account"].create(
            {
                "name": "Carbon extra-accounting",
                "code": "10001",
                "account_type": "expense",
                "company_ids": [(6, 0, [cls.env.company.id])],
            }
        )

        cls.env.company.write(
            {
                "carbon_freight_product_upstream": carbon_freight_product_upstream.id,
                "carbon_freight_product_downstream": carbon_freight_product_downstream.id,
                "carbon_freight_climatiq_api_url": "http://test_api_url",
                "carbon_freight_climatiq_api_key": "test_api_key",
                "carbon_freight_transport_mode": "road",
                "carbon_freight_journal_id": carbon_journal.id,
                "carbon_freight_account_id": carbon_account.id,
            }
        )

        cls.customer = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})

        cls.product_to_sell = cls.env["product.product"].create(
            {
                "name": "Product to Sell",
                "type": "consu",
                "weight": 1.0,
                "is_storable": True,
            }
        )
        cls.product_to_purchase = cls.env["product.product"].create(
            {
                "name": "Product to Purchase",
                "type": "consu",
                "weight": 2.0,
                "is_storable": True,
            }
        )

        product_delivery = cls.env["product.product"].create(
            {
                "name": "Delivery Charges",
                "type": "service",
                "list_price": 40.0,
                "categ_id": cls.env.ref("delivery.product_category_deliveries").id,
            }
        )
        delivery_carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Standard Delivery",
                "fixed_price": 40,
                "delivery_type": "fixed",
                "product_id": product_delivery.id,
            }
        )

        product_uom_unit = cls.env.ref("uom.product_uom_unit")
        so = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "partner_invoice_id": cls.customer.id,
                "partner_shipping_id": cls.customer.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product_to_sell.name,
                            "product_id": cls.product_to_sell.id,
                            "product_uom_qty": 10,
                            "product_uom": product_uom_unit.id,
                            "price_unit": 120.00,
                        },
                    )
                ],
            }
        )
        delivery_wizard = Form(
            cls.env["choose.delivery.carrier"].with_context(
                default_order_id=so.id, default_carrier_id=delivery_carrier.id
            )
        )
        delivery_wizard.save().button_confirm()
        so.action_confirm()
        cls.outgoing_picking = so.picking_ids[0]
        cls.outgoing_picking.shipping_weight = 10.0
        cls.outgoing_picking.write({"state": "done"})

        po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_to_purchase.id,
                            "product_qty": 5.0,
                            "price_unit": 100.0,
                            "name": "Purchase of " + cls.product_to_purchase.name,
                        },
                    )
                ],
            }
        )
        po.button_confirm()
        cls.incoming_picking = po.picking_ids[0]
        cls.incoming_picking.shipping_weight = 10.0
        cls.incoming_picking.write({"state": "done"})
