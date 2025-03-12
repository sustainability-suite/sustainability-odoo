from datetime import datetime

from odoo import Command
from odoo.tests import tagged

from odoo.addons.sustainability.tests.common import CarbonCommon


@tagged("factor_domain")
class TestsFactorDomain(CarbonCommon):
    """Test emission factor filtering based on compute method and UOM."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env["carbon.distribution.line"].search([]).unlink()
        cls.env["carbon.line.origin"].search([]).unlink()
        factors = cls.env["carbon.factor"].search([])
        factors.write({"parent_id": None, "required_type_ids": None})
        factors.unlink()

        (
            cls.carbon_factor_monetary,
            cls.carbon_factor_physical,
        ) = cls.env["carbon.factor"].create(
            [
                {"name": "Test monetary", "carbon_compute_method": "monetary"},
                {"name": "Test physical", "carbon_compute_method": "physical"},
            ]
        )

        cls.env["carbon.factor.value"].create(
            [
                {
                    "factor_id": cls.carbon_factor_monetary.id,
                    "carbon_monetary_currency_id": cls.currency_eur.id,
                    "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                    "carbon_value": 0.025,
                },
                {
                    "factor_id": cls.carbon_factor_physical.id,
                    "carbon_uom_id": cls.uom_hour.id,
                    "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                    "carbon_value": 0.022,
                },
            ]
        )

        cls.office_chair_product = cls.env["product.product"].create(
            {
                "name": "Test",
                "uom_id": cls.uom_hour.id,
                "carbon_in_is_manual": True,
                "carbon_in_factor_id": cls.carbon_factor_physical.id,
            }
        )

    def test_includes_factors_with_category_weight(self):
        """Test that factor with category weight is included"""

        factor_with_matching_uom_category = self.env["carbon.factor"].create(
            {
                "name": "Factor with Matching UOM Category",
                "carbon_compute_method": "physical",
                "value_ids": [
                    Command.create(
                        {
                            "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                            "carbon_uom_id": self.env.ref("uom.product_uom_ton").id,
                            "carbon_value": 10,
                        }
                    )
                ],
            }
        )

        factors = self.env["carbon.factor"].search(
            self.office_chair_product._get_uom_filtered_factors_domain(
                self.office_chair_product.uom_id.id
            )
        )

        self.assertIn(factor_with_matching_uom_category, factors)

    def test_includes_physical_and_monetary_factors(self):
        """Test if the domain results in factors that include both physical and monetary EFs"""
        factors = self.env["carbon.factor"].search(
            self.office_chair_product._get_uom_filtered_factors_domain(
                self.office_chair_product.uom_id.id
            )
        )

        self.assertIn(self.carbon_factor_physical, factors)
        self.assertEqual(len(factors), 2)

    def test_no_factors_for_invalid_uom(self):
        """Test that no factors are returned for an invalid UOM."""
        self.carbon_factor_monetary.unlink()
        factors = self.env["carbon.factor"].search(
            self.office_chair_product._get_uom_filtered_factors_domain(self.uom_day.id)
        )
        self.assertFalse(factors)
