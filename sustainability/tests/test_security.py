from odoo.addons.sustainability.tests.common import CarbonCommon
import odoo.tests.common as common
from odoo.exceptions import AccessError

MODELS_LIST = [ # TODO: Automate this list
    "carbon.factor",
    "carbon.factor.database",
    "carbon.factor.contributor",
    "carbon.factor.value",
    "carbon.factor.value.report",
    "carbon.factor.type",
    "carbon.distribution.line",
    "carbon.line.origin",
    "sustainability.scenario",
    "sustainability.action.plan",
    "sustainability.action",
    "sustainability.nomenclature",
    "sustainability.nomenclature.category",
    "sustainability.nomenclature.sub_category", # TODO: If we can we need to remove the _ so we can automate the test
    "sustainability.nomenclature.reporting",
    "sustainability.approach",
    "sustainability.approach.characterization",
]


class TestCarbonSecurity(CarbonCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a test user with specific groups
        cls.sustainability_test_user = common.new_test_user(
            env=cls.env, login="sustainability_test_user", groups="base.group_user,account.group_account_manager"
        )
        
        # Create a test user with admin groups
        cls.sustainability_admin_user = common.new_test_user(
            env=cls.env, login="sustainability_admin_user", groups="base.group_user,sustainability.group_sustainability_admin,account.group_account_manager"
        )
    
    def test_user_permissions(self):
        # Check if the user has access to the sustainability model
        for model_name in MODELS_LIST:
            model = self.env[model_name].with_user(self.sustainability_test_user)
            self.assertTrue(model.check_access_rights('read', raise_exception=False))
            self.assertFalse(model.check_access_rights('write', raise_exception=False))
            self.assertFalse(model.check_access_rights('create', raise_exception=False))
            self.assertFalse(model.check_access_rights('unlink', raise_exception=False))

    def test_admin_permissions(self):
        # Check if the admin user has full access to the sustainability model
        for model_name in MODELS_LIST:
            model = self.env[model_name].with_user(self.sustainability_admin_user)
            self.assertTrue(model.check_access_rights('read', raise_exception=False))
            self.assertTrue(model.check_access_rights('write', raise_exception=False))
            self.assertTrue(model.check_access_rights('create', raise_exception=False))
            self.assertTrue(model.check_access_rights('unlink', raise_exception=False))
            
    def test_account_move_line_write_user_permissions(self):
        with self.assertRaises(AccessError):
            self.env['account.move.line'].search([], limit=1).with_user(self.sustainability_test_user).write(dict(carbon_debt=100))
        
    def test_account_move_line_write_admin_permissions(self):
        self.env['account.move.line'].search([], limit=1).with_user(self.sustainability_admin_user).write(dict(carbon_debt=100))
