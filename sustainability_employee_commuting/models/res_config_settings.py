from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    employee_commuting_carbon_factor_id = fields.Many2one(
        "carbon.factor",
        related="company_id.employee_commuting_carbon_factor_id",
        readonly=False,
    )
    employee_commuting_journal_id = fields.Many2one(
        "account.journal",
        related="company_id.employee_commuting_journal_id",
        readonly=False,
    )
    employee_commuting_account_id = fields.Many2one(
        "account.account",
        related="company_id.employee_commuting_account_id",
        readonly=False,
    )
    employee_commuting_carbon_cronjob_active = fields.Boolean(
        "Cron job active",
        related="company_id.employee_commuting_carbon_cronjob_active",
        readonly=False,
    )
    employee_remote_work_carbon_factor_id = fields.Many2one(
        "carbon.factor",
        related="company_id.employee_remote_work_carbon_factor_id",
        readonly=False,
        domain=lambda self: [
            ("carbon_uom_id", "=", self.env.ref("uom.product_uom_day").id)
        ],
    )
    employee_remote_work_journal_id = fields.Many2one(
        "account.journal",
        related="company_id.employee_remote_work_journal_id",
        readonly=False,
    )
    employee_remote_work_account_id = fields.Many2one(
        "account.account",
        related="company_id.employee_remote_work_account_id",
        readonly=False,
    )
    employee_remote_work_carbon_cronjob_active = fields.Boolean(
        "Cron job",
        related="company_id.employee_remote_work_carbon_cronjob_active",
        readonly=False,
    )

    def set_values(self):
        res = super().set_values()

        self._set_cron_active(
            "sustainability_employee_commuting.cron_carbon_employee_commuting_account_move_create",
            self.employee_commuting_carbon_cronjob_active,
        )

        self._set_cron_active(
            "sustainability_employee_commuting.cron_carbon_employee_remote_work_account_move_create",
            self.employee_remote_work_carbon_cronjob_active,
        )

        return res

    def _set_cron_active(self, cron_reference, is_active):
        cron = self.env.ref(cron_reference).sudo()
        if cron and is_active:
            cron.active = True
