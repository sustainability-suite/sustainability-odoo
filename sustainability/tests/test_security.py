import odoo.tests.common as common
from odoo.exceptions import AccessError

from odoo.addons.sustainability.tests.common import CarbonCommon

MODELS_LIST = [  # TODO: Automate this list
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
    "sustainability.nomenclature.sub_category",  # TODO: If we can we need to remove the _ so we can automate the test
    "sustainability.nomenclature.reporting",
    "sustainability.approach",
    "sustainability.approach.characterization",
]
MIXIN_MODELS = ["common.mixin", "carbon.mixin", "carbon.line.mixin"]

SKIP_MODELS = [
    "account.account",  # Only one group with write access so we can't properly test the write access
    "account.move.line",  # TODO: Find a way to test this model, currently not possible
]


class TestCarbonSecurity(CarbonCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        common_groups = "base.group_user,account.group_account_manager"
        test_groups = common_groups
        admin_groups = (
            common_groups
            + ",sustainability.group_sustainability_admin,base.group_system"
        )
        # Create a test user with specific groups
        cls.sustainability_test_user = common.new_test_user(
            env=cls.env, login="sustainability_test_user", groups=test_groups
        )

        # Create a test user with admin groups
        cls.sustainability_admin_user = common.new_test_user(
            env=cls.env, login="sustainability_admin_user", groups=admin_groups
        )

    def test_user_permissions(self):
        # Check if the user has access to the sustainability model
        for model_name in MODELS_LIST:
            model = self.env[model_name].with_user(self.sustainability_test_user)
            self.assertTrue(model.check_access_rights("read", raise_exception=False))
            self.assertFalse(model.check_access_rights("write", raise_exception=False))
            self.assertFalse(model.check_access_rights("create", raise_exception=False))
            self.assertFalse(model.check_access_rights("unlink", raise_exception=False))

    def test_admin_permissions(self):
        # Check if the admin user has full access to the sustainability model
        for model_name in MODELS_LIST:
            model = self.env[model_name].with_user(self.sustainability_admin_user)
            self.assertTrue(model.check_access_rights("read", raise_exception=False))
            self.assertTrue(model.check_access_rights("write", raise_exception=False))
            self.assertTrue(model.check_access_rights("create", raise_exception=False))
            self.assertTrue(model.check_access_rights("unlink", raise_exception=False))

    def test_mixin_models_write_user_permissions(self):
        test_user = self.sustainability_test_user
        for model in self.env:
            model = self.env[model].with_user(test_user)
            if "mixin" in model._name or model._name in SKIP_MODELS:
                continue
            if any(mixin in model._inherit for mixin in MIXIN_MODELS) or any(
                mixin in model._inherits for mixin in MIXIN_MODELS
            ):
                fields = model._get_carbon_fields_name()
                records = model.search([], limit=10)
                for field in fields:
                    _field = model._fields.get(field)
                    if _field.compute:
                        continue
                    for record in records:
                        with self.assertRaises(AccessError):
                            record.with_user(test_user).write(
                                {field: False}
                            )  # False should be available for all fields type

    def test_mixin_models_write_admin_permissions(self):
        test_user = self.sustainability_admin_user
        for model in self.env:
            model = self.env[model].with_user(test_user)
            if "mixin" in model._name or model._name in SKIP_MODELS:
                continue
            if any(mixin in model._inherit for mixin in MIXIN_MODELS) or any(
                mixin in model._inherits for mixin in MIXIN_MODELS
            ):
                fields = model._get_carbon_fields_name()
                records = model.search([], limit=10)
                for field in fields:
                    _field = model._fields.get(field)
                    if _field.compute:
                        continue
                    for record in records:
                        record.with_user(test_user).write(
                            {field: False}
                        )  # False should be available for all fields type
