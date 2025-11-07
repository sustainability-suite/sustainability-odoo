from datetime import datetime

from odoo import Command

from odoo.addons.sustainability.tests.common import CarbonCommon


class CarbonPurchaseCommon(CarbonCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Carbon Factors
        cls.purchase_carbon_factor_monetary_1 = cls.env["carbon.factor"].create(
            dict(
                name="Test monetary purchase 1",
                carbon_compute_method="monetary",
                value_ids=[
                    Command.create(
                        dict(
                            carbon_monetary_currency_id=cls.currency_usd.id,
                            date=datetime.today().strftime("%Y-%m-%d %H:%M"),
                            carbon_value=5,
                        )
                    ),
                ],
            )
        )
        cls.purchase_carbon_factor_monetary_product_1 = cls.env["carbon.factor"].create(
            dict(
                name="Test monetary purchase 1 product",
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
        cls.purchase_carbon_factor_monetary_2 = cls.env["carbon.factor"].create(
            dict(
                name="Test monetary purchase 2",
                carbon_compute_method="monetary",
                value_ids=[
                    Command.create(
                        dict(
                            carbon_monetary_currency_id=cls.currency_usd.id,
                            date=datetime.today().strftime("%Y-%m-%d %H:%M"),
                            carbon_value=10,
                        )
                    ),
                ],
            )
        )
        cls.purchase_carbon_factor_monetary_3 = cls.env["carbon.factor"].create(
            dict(
                name="Test monetary purchase 3",
                carbon_compute_method="monetary",
                value_ids=[
                    Command.create(
                        dict(
                            carbon_monetary_currency_id=cls.currency_usd.id,
                            date=datetime.today().strftime("%Y-%m-%d %H:%M"),
                            carbon_value=15,
                        )
                    ),
                ],
            )
        )
        cls.purchase_carbon_factor_monetary_4 = cls.env["carbon.factor"].create(
            dict(
                name="Test monetary purchase 4",
                carbon_compute_method="monetary",
                value_ids=[
                    Command.create(
                        dict(
                            carbon_monetary_currency_id=cls.currency_usd.id,
                            date=datetime.today().strftime("%Y-%m-%d %H:%M"),
                            carbon_value=20,
                        )
                    ),
                ],
            )
        )

        # Partners
        cls.purchase_partner_1 = cls.env["res.partner"].create(
            dict(
                name="Test Partner number",
                email="test.partner.purchase@example.com",
                phone="+123456782",
                street="123 Test Street",
                city="Test City 2",
                country_id=cls.env.ref("base.us").id,
            )
        )
        cls.purchase_partner_2 = cls.env["res.partner"].create(
            dict(
                name="Test Partner number 2",
                email="test.partner.purchase2@example.com",
                phone="+123456782",
                street="123 Test Street 2",
                city="Test City 2",
                country_id=cls.env.ref("base.us").id,
            )
        )
        cls.purchase_partner_3 = cls.env["res.partner"].create(
            dict(
                name="Test Partner number 3",
                email="test.partner.purchase3@example.com",
                phone="+133456783",
                street="133 Test Street 3",
                city="Test City 3",
                country_id=cls.env.ref("base.us").id,
                carbon_in_factor_id=cls.purchase_carbon_factor_monetary_3.id,
            )
        )
        cls.purchase_partner_4 = cls.env["res.partner"].create(
            dict(
                name="Test Partner number 4",
                email="test.partner.purchase4@example.com",
                phone="+144456784",
                street="144 Test Street 4",
                city="Test City 4",
                country_id=cls.env.ref("base.us").id,
            )
        )

        # Product Template
        cls.purchase_product_category_1 = cls.env["product.category"].create(
            dict(
                name="Test Product Category",
            )
        )
        cls.kg_uom_id = cls.env.ref("uom.product_uom_kgm")
        cls.purchase_product_template_1 = cls.env[
            "product.template"
        ].create(
            dict(
                categ_id=cls.purchase_product_category_1.id,
                name="Wooden Chair",
                uom_id=cls.kg_uom_id.id,
                list_price=100,
                carbon_in_factor_id=cls.purchase_carbon_factor_monetary_product_1.id,
                carbon_in_is_manual=True,  # TODO: Should not be there... Fix in carbon_mixin.py
                carbon_in_mode="manual",  # TODO: Should not be there... Fix in carbon_mixin.py
                seller_ids=[
                    Command.create(
                        dict(
                            currency_id=cls.currency_usd.id,
                            delay=0,
                            min_qty=1,
                            partner_id=cls.purchase_partner_1.id,
                            price=100,
                            carbon_in_factor_id=cls.purchase_carbon_factor_monetary_1.id,
                        )
                    ),
                    Command.create(
                        dict(
                            currency_id=cls.currency_usd.id,
                            delay=0,
                            min_qty=1,
                            partner_id=cls.purchase_partner_2.id,
                            price=100,
                            carbon_in_factor_id=cls.purchase_carbon_factor_monetary_2.id,
                        )
                    ),
                    Command.create(
                        dict(
                            currency_id=cls.currency_usd.id,
                            delay=0,
                            min_qty=1,
                            partner_id=cls.purchase_partner_3.id,
                            price=100,
                        )
                    ),
                ],
            )
        )
        cls.purchase_product_template_2 = cls.purchase_product_template_1.copy()
        cls.purchase_product_template_2.write(
            dict(
                name="Wooden Table",
                seller_ids=[],
                carbon_in_factor_id=cls.purchase_carbon_factor_monetary_2.id,
                carbon_in_is_manual=True,
                carbon_in_mode="manual",
            )
        )
        cls.purchase_product_template_3 = cls.purchase_product_template_1.copy()
        cls.purchase_product_template_3.write(
            dict(
                name="Wooden Fork",
                seller_ids=[],
                carbon_in_factor_id=cls.purchase_carbon_factor_monetary_3.id,
                carbon_in_is_manual=True,
                carbon_in_mode="manual",
            )
        )
        cls.purchase_product_template_4 = cls.purchase_product_template_1.copy()
        cls.purchase_product_template_4.write(
            dict(
                name="Wooden Spoon",
                seller_ids=[],
                carbon_in_factor_id=cls.purchase_carbon_factor_monetary_4.id,
                carbon_in_is_manual=True,
                carbon_in_mode="manual",
            )
        )

        # Product Product
        cls.purchase_product_product_1 = cls.env["product.product"].search(
            [("product_tmpl_id", "=", cls.purchase_product_template_1.id)], limit=1
        )
        cls.purchase_product_product_2 = cls.env["product.product"].search(
            [("product_tmpl_id", "=", cls.purchase_product_template_2.id)], limit=1
        )
        cls.purchase_product_product_3 = cls.env["product.product"].search(
            [("product_tmpl_id", "=", cls.purchase_product_template_3.id)], limit=1
        )
        cls.purchase_product_product_4 = cls.env["product.product"].search(
            [("product_tmpl_id", "=", cls.purchase_product_template_4.id)], limit=1
        )

        # Purchase Order
        cls.purchase_purchase_order = cls.env["purchase.order"]
        cls.purchase_purchase_order_1 = cls.env["purchase.order"].create(
            dict(
                partner_id=cls.purchase_partner_1.id,
                order_line=[
                    Command.create(
                        dict(
                            product_id=cls.purchase_product_product_1.id,
                            product_qty=1.0,
                            product_uom_id=cls.kg_uom_id.id,
                            price_unit=100.0,
                        )
                    ),
                ],
            )
        )
        cls.purchase_purchase_order |= cls.purchase_purchase_order_1
        cls.purchase_purchase_order_2 = cls.purchase_purchase_order_1.copy()
        cls.purchase_purchase_order |= cls.purchase_purchase_order_2
        cls.purchase_purchase_order_2.write(
            dict(
                partner_id=cls.purchase_partner_2.id,
            )
        )
        cls.purchase_purchase_order_2.order_line[0].write(
            dict(
                product_id=cls.purchase_product_product_2.id,
            )
        )

        cls.purchase_purchase_order_3 = cls.purchase_purchase_order_1.copy()
        cls.purchase_purchase_order |= cls.purchase_purchase_order_3
        cls.purchase_purchase_order_3.write(
            dict(
                partner_id=cls.purchase_partner_3.id,
            )
        )
        cls.purchase_purchase_order_3.order_line[0].write(
            dict(
                product_id=cls.purchase_product_product_3.id,
            )
        )
        cls.purchase_purchase_order_4 = cls.purchase_purchase_order_1.copy()
        cls.purchase_purchase_order |= cls.purchase_purchase_order_4
        cls.purchase_purchase_order_4.write(
            dict(
                partner_id=cls.purchase_partner_4.id,
            )
        )
        cls.purchase_purchase_order_4.order_line[0].write(
            dict(
                product_id=cls.purchase_product_product_4.id,
            )
        )
        cls.purchase_purchase_order_5 = cls.purchase_purchase_order_1.copy()
        cls.purchase_purchase_order |= cls.purchase_purchase_order_5

        cls.purchase_purchase_order_6 = cls.purchase_purchase_order_1.copy()
        cls.purchase_purchase_order |= cls.purchase_purchase_order_6
