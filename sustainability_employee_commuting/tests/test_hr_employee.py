from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class EmployeeCommutingTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.employee_commuting_test_employee = cls.env['hr.employee'].create({
                'name': 'Test Employee',
            })
        
        cls.employee_commuting_commuting_metro = cls.env['carbon.hr.commuting'].create({
                'carbon_factor_id': cls.env.ref('sustainability.carbon_factor_metro').id,
                'distance_km': 10,
                'employee_id': cls.employee_commuting_test_employee.id,
            })
        cls.employee_commuting_commuting_bus = cls.env['carbon.hr.commuting'].create({
                'carbon_factor_id': cls.env.ref('sustainability.carbon_factor_bus').id,
                'distance_km': 10,
                'employee_id': cls.employee_commuting_test_employee.id,
            })
        cls.employee_commuting_commuting_bycicle = cls.env['carbon.hr.commuting'].create({
                'carbon_factor_id': cls.env.ref('sustainability.carbon_factor_bicycle').id,
                'distance_km': 10,
                'employee_id': cls.employee_commuting_test_employee.id,
            })


    def test_get_carbon_commuting_line_vals_no_end_dates(self):
        """
        Test the method _get_carbon_commuting_line_vals when no commuting records have end dates
        """
        date = False # Set to datetime.now() in the method
        vals = self.employee_commuting_test_employee._get_carbon_commuting_line_vals(date)

        self.assertTrue(self.employee_commuting_commuting_metro.carbon_factor_id.name in vals['name'], f"The name of the carbon line should contain {self.employee_commuting_commuting_metro.carbon_factor_id.name}")
        self.assertTrue(self.employee_commuting_commuting_bus.carbon_factor_id.name in vals['name'], f"The name of the carbon line should contain {self.employee_commuting_commuting_bus.carbon_factor_id.name}")
        self.assertTrue(self.employee_commuting_commuting_bycicle.carbon_factor_id.name in vals['name'], f"The name of the carbon line should contain {self.employee_commuting_commuting_bycicle.carbon_factor_id.name}")

    def test_get_carbon_commuting_line_vals_with_end_dates(self):
        """
        Test the method _get_carbon_commuting_line_vals when some commuting records are
        only valid for past/futur period
        """
        self.employee_commuting_commuting_metro.start_date, self.employee_commuting_commuting_metro.end_date = '1995-01-01', '1995-12-01' # Should not be considered (already ended)
        self.employee_commuting_commuting_bus.start_date = '2995-01-01' # Should not be considered (did not began yet). update test before 2995 ;)

        date = False # Set to datetime.now() in the method
        vals = self.employee_commuting_test_employee._get_carbon_commuting_line_vals(date)

        self.assertTrue(self.employee_commuting_commuting_bycicle.carbon_factor_id.name in vals['name'], f"The name of the carbon line should contain {self.employee_commuting_commuting_bycicle.carbon_factor_id.name}")
        self.assertTrue(self.employee_commuting_commuting_bus.carbon_factor_id.name not in vals['name'], f"The name of the carbon line should not contain {self.employee_commuting_commuting_bus.carbon_factor_id.name}")
        self.assertTrue(self.employee_commuting_commuting_metro.carbon_factor_id.name not in vals['name'], f"The name of the carbon line should not contain {self.employee_commuting_commuting_metro.carbon_factor_id.name}")
