from datetime import datetime

from odoo import Command

from odoo.addons.sustainability.tests.common import CarbonCommon


class CarbonSaleCommon(CarbonCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sale_carbon_factor_monetary_product_1 = cls.env["carbon.factor"].create(
            dict(
                name="Test monetary sale 1 product",
                carbon_compute_method="monetary",
                value_ids=[
                    Command.create(
                        dict(
                            carbon_monetary_currency_id=cls.currency_usd.id,
                            date=datetime.today().strftime("%Y-%m-%d %H:%M"),
                            carbon_value=25,
                        )
                    ),
                ],
            )
        )

        cls.sale_partner_1 = cls.env["res.partner"].create(
            dict(
                name="Test Customer 1",
                email="test.customer.sale@example.com",
                phone="+123456782",
                street="123 Test Street",
                city="Test City 1",
                country_id=cls.env.ref("base.us").id,
            )
        )

        cls.sale_product_category_1 = cls.env["product.category"].create(
            dict(
                name="Test Sale Product Category",
            )
        )
        cls.kg_uom_id = cls.env.ref("uom.product_uom_kgm")
        cls.sale_product_template_1 = cls.env["product.template"].create(
            dict(
                categ_id=cls.sale_product_category_1.id,
                name="Wooden Chair (Sale)",
                uom_id=cls.kg_uom_id.id,
                uom_po_id=cls.kg_uom_id.id,
                list_price=100,
                carbon_out_factor_id=cls.sale_carbon_factor_monetary_product_1.id,
                carbon_out_is_manual=True,
                carbon_out_mode="manual",
            )
        )

        cls.sale_product_product_1 = cls.env["product.product"].search(
            [("product_tmpl_id", "=", cls.sale_product_template_1.id)], limit=1
        )

        cls.sale_order = cls.env["sale.order"]
        cls.sale_order_1 = cls.env["sale.order"].create(
            dict(
                partner_id=cls.sale_partner_1.id,
                order_line=[
                    Command.create(
                        dict(
                            product_id=cls.sale_product_product_1.id,
                            product_uom_qty=1.0,
                            product_uom=cls.kg_uom_id.id,
                            price_unit=100.0,
                        )
                    ),
                ],
            )
        )
        cls.sale_order |= cls.sale_order_1
