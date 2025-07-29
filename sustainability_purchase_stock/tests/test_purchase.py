from odoo import Command

from odoo.addons.sustainability_purchase.tests.common import CarbonPurchaseCommon


class TestSustainabilityPurchaseStock(CarbonPurchaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.delivery_contact = cls.env["res.partner"].create(
            {
                "parent_id": cls.purchase_partner_1.id,
                "type": "delivery",
                "name": "Delivery Contact",
            }
        )
        cls.po = (
            cls.env["purchase.order"]
            .with_context(force_onchange=True)
            .create(
                {
                    "partner_id": cls.purchase_partner_1.id,
                }
            )
        )
        cls.po._onchange_partner_id_set_sustainability_shipping()
        cls.po_with_shipping = cls.env["purchase.order"].create(
            {
                "partner_id": cls.purchase_partner_1.id,
                "sustainability_partner_shipping_id": cls.purchase_partner_2.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.purchase_product_product_1.id,
                            "product_qty": 1.0,
                            "product_uom": cls.kg_uom_id.id,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )

    def test_delivery_address_field(self):
        po = self.po
        addresses = self.purchase_partner_1.address_get(["delivery"])
        delivery_id = addresses.get("delivery")
        expected_id = delivery_id or self.purchase_partner_1.id

        self.assertEqual(
            po.sustainability_partner_shipping_id.id,
            expected_id,
            "Default delivery address should match address_get result",
        )

        custom_address = self.purchase_partner_2
        po.sustainability_partner_shipping_id = custom_address
        self.assertEqual(
            po.sustainability_partner_shipping_id,
            custom_address,
            "Should be able to set custom delivery address",
        )

    def test_delivery_address_propagation_to_picking(self):
        po = self.po_with_shipping
        po.button_confirm()
        if po.picking_ids:
            picking = po.picking_ids[0]
            self.assertEqual(
                picking.partner_id,
                po.sustainability_partner_shipping_id,
                "Picking partner should match PO delivery address",
            )
