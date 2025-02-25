from odoo.tests import HttpCase, tagged


@tagged("post_install_l10n", "post_install", "-at_install", "sustainability_tour")
class TestUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Activate full accounting features
        admin_user = cls.env.ref("base.user_admin")
        accounting_group = cls.env.ref("account.group_account_user")
        accounting_group.users = [(4, admin_user.id)]

    def test_create_journal_entry(self):
        self.start_tour("/web", "create_journal_entry", login="admin")
