from odoo.addons.sustainability_employee_commuting.tests.common import CarbonCommon


class TestCommuting(CarbonCommon):
    def test_carbon_commuting(self):
        """Test that the cron job processes carbon commuting correctly."""

        self.env.company._cron_carbon_account_move_create("commuting")

        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id.ref", "ilike", "Employee_Commuting"),
            ],
        )
        total_value = sum(origin.signed_value for origin in carbon_line_origins)

        expected_result = 35.2

        self.assertEqual(
            round(total_value, 2),
            expected_result,
            f"Expected a value of {expected_result} for the carbon line origin.",
        )

    def test_carbon_remote_work(self):
        """
        Test carbon emission computation for remote work with different employee setups:
        - Employee with only a home location
        - Employee with only an office location
        - Employee without a work location
        - Employee without a new contract
        - Employee without a contract
        """
        self.env.company._cron_carbon_account_move_create("remote_work")

        carbon_line_origins = self.env["carbon.line.origin"].search(
            [
                ("move_id.ref", "ilike", "Remote_Work"),
            ],
        )
        total_value = sum(origin.signed_value for origin in carbon_line_origins)

        expected_result = 54.67

        self.assertEqual(
            round(total_value, 2),
            expected_result,
            f"Expected a value of {expected_result} for the carbon line origin.",
        )
