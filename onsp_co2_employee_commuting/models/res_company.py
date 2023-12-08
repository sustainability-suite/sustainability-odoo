import logging
from datetime import datetime, time

from dateutil.rrule import MONTHLY, rrule, rruleset

from odoo import fields, models

from .hr_employee import WEEKS_PER_MONTH

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    employee_commuting_carbon_factor_id = fields.Many2one("carbon.factor")
    employee_commuting_journal_id = fields.Many2one("account.journal")
    employee_commuting_account_id = fields.Many2one(
        "account.account",
        string="Employee Commuting Account",
        domain="[('deprecated', '=', False)]",
    )
    employee_commuting_carbon_cronjob_active = fields.Boolean(
        string="Cronjob active", default=False
    )

    def _cron_carbon_commuting_account_move_create(self):
        for company in self.env["res.company"].search(
            [("employee_commuting_carbon_cronjob_active", "=", True)]
        ):
            if (
                not company.employee_commuting_journal_id
                or not company.employee_commuting_account_id
            ):
                continue

            # Get date at which it should start
            last_account_move = self.env["account.move"].search(
                [
                    ("company_id", "=", company.id),
                    ("is_employee_commuting_carbon", "=", True),
                ],
                order="employee_commuting_carbon_date DESC",
                limit=1,
            )
            last_account_move_date = (
                datetime.combine(
                    last_account_move.employee_commuting_carbon_date, time(1, 00)
                )
                if last_account_move
                else datetime.combine(company.carbon_lock_date, time(1, 00))
                if company.carbon_lock_date
                else datetime.now().replace(day=1, month=1)
            )

            # Check all months between last account_move and now
            date_set = rruleset()
            date_set.rrule(
                rrule(
                    MONTHLY,
                    bymonthday=(-1),
                    dtstart=last_account_move_date,
                    until=datetime.now(),
                )
            )
            date_set.exdate(last_account_move_date)
            for account_move_date in list(date_set):
                account_move_creation_success = (
                    company.carbon_commuting_create_account_move(
                        account_move_date=account_move_date
                    )
                )
                # stop if it didn't work in order to not have any skipped month
                if not account_move_creation_success:
                    break

    def carbon_commuting_create_account_move(self, account_move_date):
        self.ensure_one()
        company = self
        try:
            # Get all employees with active contract at the date
            employees = (
                self.env["hr.employee"]
                .search([("company_id", "=", company.id)])
                ._get_all_contracts(
                    account_move_date, account_move_date, states=["open", "close"]
                )
            ).employee_id
            if not employees:
                return False

            employees_with_commuting = employees.filtered("carbon_commuting_ids")
            decimal_precision = self.env["decimal.precision"].precision_get(
                "Carbon value"
            )

            company_commuting_carbon_value = 0
            company_commuting_km = 0
            aml_vals_list = []

            # Erase existing ones for this date to avoid duplicates
            account_moves = self.env["account.move"].search(
                [
                    ("company_id", "=", company.id),
                    ("is_employee_commuting_carbon", "=", True),
                    ("employee_commuting_carbon_date", "=", account_move_date),
                ]
            )
            account_moves.unlink()

            for employee in employees_with_commuting:
                aml_vals = employee._get_carbon_commuting_line_vals(account_move_date)
                company_commuting_carbon_value += aml_vals.get("carbon_debt")
                company_commuting_km += sum(
                    employee.carbon_commuting_ids.mapped("distance_km")
                    * WEEKS_PER_MONTH
                )
                aml_vals_list.append((0, 0, aml_vals))

            average_carbon_per_km = (
                company_commuting_carbon_value / company_commuting_km
                if company_commuting_km
                else 0
            )

            for employee in employees - employees_with_commuting:
                if employee.km_home_work:
                    # 4 weeks per month
                    commuting_carbon = (
                        employee.km_home_work
                        * 10
                        * average_carbon_per_km
                        * WEEKS_PER_MONTH
                    )
                    commuting_details = f"\n| {employee.km_home_work * 10} Km"
                else:
                    commuting_carbon = (
                        company_commuting_carbon_value / len(employees_with_commuting)
                        if len(employees_with_commuting)
                        else 0
                    )
                    commuting_details = f"\n| {round(company_commuting_carbon_value / len(employees_with_commuting) if len(employees_with_commuting) else 0, decimal_precision)} -> Company average emission for commuting"

                aml_vals = employee._get_carbon_commuting_line_vals(account_move_date)
                aml_vals.update(
                    {
                        "carbon_debt": commuting_carbon,
                        "name": f"{employee.name}{commuting_details}",
                    }
                )
                aml_vals_list.append((0, 0, aml_vals))

            self.env["account.move"].create(
                {
                    "ref": f'Employee_Commuting_Carbon_{account_move_date.strftime("%Y%m")}',
                    "journal_id": company.employee_commuting_journal_id.id,
                    "date": account_move_date.strftime("%Y-%m-%d"),
                    "partner_id": company.partner_id.id,
                    "company_id": company.id,
                    "invoice_line_ids": aml_vals_list,
                    "move_type": "in_invoice",
                    "is_employee_commuting_carbon": True,
                    "employee_commuting_carbon_date": account_move_date.strftime(
                        "%Y-%m-%d"
                    ),
                }
            )
            return True

        except Exception as e:
            notification_message = (
                f"Error processing employee {employee.name}: {str(e)}."
            )
            _logger.info(notification_message)
            employee.message_post(
                body=notification_message,
                subject=f"Error Notification : Commuting Carbon print on the {account_move_date.strftime('%Y-%m-%d')}",
            )
            return False
