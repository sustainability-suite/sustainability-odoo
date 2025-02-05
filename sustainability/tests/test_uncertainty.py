from odoo.addons.sustainability.tests.common import CarbonCommon


class TestsCarbonUncertainty(CarbonCommon):
    def test_uncertainty(self):
        uncertainty_percentage = self.env["carbon.factor"]._get_uncertainty_value(
            0.05, 0.1
        )

        self.assertEqual(
            uncertainty_percentage,
            0.1118033988749895,
            f"Carbon factor uncertainty computation is wrong. Should be 0.1118033988749895 not {uncertainty_percentage}",
        )
