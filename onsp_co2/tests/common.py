from odoo.tests import TransactionCase, tagged


class CarbonCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.uom_hour = cls.env.ref('uom.product_uom_hour')
        cls.uom_day = cls.env.ref('uom.product_uom_day')
        cls.currency_eur = cls.env.ref('base.EUR')
        cls.currency_usd = cls.env.ref('base.USD')

        # Company
        cls.env.company.write({
            'carbon_in_value': 0.022,
            'carbon_out_value': 0.025,
            'currency_id': cls.currency_usd.id,
        })
        # Product category
        cls.env.ref('product.product_category_all').write({
            'carbon_in_is_manual': True,
            'carbon_in_compute_method': 'monetary',
            'carbon_in_value': 0.15,
            'carbon_in_monetary_currency_id': cls.currency_eur.id,
        })

        cls.env['res.currency.rate'].search([]).unlink()
        cls.env['res.currency.rate'].create([
            {
                'name': '2010-01-01',
                'company_rate': 1,
                'inverse_company_rate': 1,
                'rate': 1,
                'currency_id': cls.currency_usd.id,
            },
            {
                'name': '2023-01-01',
                'company_rate': 0.952380952381,
                'currency_id': cls.currency_eur.id,
            },
        ])


        # cls.group_uom = cls.env.ref('uom.group_uom')

    # @classmethod
    # def _enable_uom(cls):
    #     cls.env.user.groups_id += cls.group_uom
    #
    # @classmethod
    # def _disable_uom(cls):
    #     cls.env.user.groups_id -= cls.group_uom
