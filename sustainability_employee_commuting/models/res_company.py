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
    employee_remote_work_carbon_factor_id = fields.Many2one("carbon.factor")
    employee_remote_work_journal_id = fields.Many2one("account.journal")
    employee_remote_work_account_id = fields.Many2one(
        "account.account",
        string="Employee Remote Work Account",
        domain="[('deprecated', '=', False)]",
    )
    employee_remote_work_carbon_cronjob_active = fields.Boolean(
        string="Remote Work Cronjob Active", default=False
    )
    employee_commuting_post_account_move_active = fields.Boolean(
        string="Post account move when cron is finished", default=False
    )

    def _cron_carbon_account_move_create(self, mode, to_post=False):
        valid_modes = ["commuting", "remote_work"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Expected one of {valid_modes}.")

        if not to_post:
            to_post = self.employee_commuting_post_account_move_active

        active_field = f"employee_{mode}_carbon_cronjob_active"
        journal_field = f"employee_{mode}_journal_id"
        account_field = f"employee_{mode}_account_id"
        carbon_date_field = f"employee_{mode}_carbon_date"
        move_type_field = f"is_employee_{mode}_carbon"

        for company in self.env["res.company"].search([(active_field, "=", True)]):
            if not getattr(company, journal_field) or not getattr(
                company, account_field
            ):
                _logger.warning(
                    f"Skipping company {company.name} (ID {company.id}): Missing journal or account for {mode}."
                )
                continue

            # Get date at which it should start
            last_account_move = self.env["account.move"].search(
                [
                    ("company_id", "=", company.id),
                    (move_type_field, "=", True),
                ],
                order=f"{carbon_date_field} DESC",
                limit=1,
            )
            last_account_move_date = (
                datetime.combine(
                    getattr(last_account_move, carbon_date_field), time(1, 0)
                )
                if last_account_move
                else (
                    datetime.combine(company.carbon_lock_date, time(1, 0))
                    if company.carbon_lock_date
                    else datetime.now().replace(day=1, month=1)
                )
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
                _logger.info(
                    f"Processing {mode} account move for date: {account_move_date}"
                )

                if mode == "commuting":
                    success = company.carbon_commuting_create_account_move(
                        account_move_date=account_move_date, to_post=to_post
                    )
                elif mode == "remote_work":
                    success = company.remote_work_create_account_move(
                        account_move_date=account_move_date, to_post=to_post
                    )
                else:
                    success = False

                if not success:
                    _logger.error(
                        f"Failed to create {mode} account move for company {company.name} on {account_move_date}"
                    )
                    break

    def delete_existing_account_moves(self, account_move_date, mode):
        """
        Deletes existing account moves for a given date to avoid duplicates.
        """
        account_moves = self.env["account.move"].search(
            [
                ("company_id", "=", self.id),
                (f"is_employee_{mode}_carbon", "=", True),
                (f"employee_{mode}_carbon_date", "=", account_move_date),
            ]
        )
        account_moves.unlink()

    def get_employees_with_contracts(self, employees_domain=None):
        """
        Retrieves employees with active contracts in the company.
        """
        employees_domain = employees_domain or []
        employees = self.env["hr.employee"].search(
            [("company_id", "=", self.id), *employees_domain]
        )
        contracts = self.env["hr.contract"].search(
            [
                ("employee_id", "in", employees.ids),
                ("state", "in", ["open", "close"]),
            ]
        )
        return contracts.mapped("employee_id")

    def calculate_average(self, metric_sum, count):
        """
        Calculates the average of a given metric if the count is non-zero.
        """
        return metric_sum / count if count else 0

    def prepare_account_move_line(
        self, employee, carbon_value, account_id, description
    ):
        """
        Prepares account move line dictionary for an employee.
        """
        return {
            "carbon_debt": carbon_value,
            "carbon_uncertainty_value": 0,
            "carbon_data_uncertainty_percentage": 0,
            "name": description,
            "account_id": account_id,
            "debit": 0,
            "credit": 0,
            "carbon_is_locked": True,
            "partner_id": employee.user_partner_id.id
            or employee.address_id.id
            or False,
            "carbon_origin_json": {
                "mode": "manual",
                "details": {"uid": self.env.uid, "username": self.env.user.name},
            },
        }

    def create_account_move(
        self, ref, journal_id, account_move_date, aml_vals_list, mode
    ):
        """
        Creates an account move with the given parameters.
        """
        valid_modes = ["commuting", "remote_work"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Expected one of {valid_modes}.")

        account_move = self.env["account.move"].create(
            {
                "ref": ref,
                "journal_id": journal_id,
                "invoice_date": account_move_date.strftime("%Y-%m-%d"),
                "date": account_move_date.strftime("%Y-%m-%d"),
                "partner_id": self.partner_id.id,
                "company_id": self.id,
                "line_ids": aml_vals_list,
                "move_type": "in_invoice",
                f"is_employee_{mode}_carbon": True,
                f"employee_{mode}_carbon_date": account_move_date.strftime("%Y-%m-%d"),
            }
        )
        return account_move

    def carbon_commuting_create_account_move(self, account_move_date, to_post=False):
        self.ensure_one()
        try:
            # Fetch employees with contracts
            employees = self.get_employees_with_contracts()
            if not employees:
                return False

            # Erase existing account moves for this date to avoid duplicates
            self.delete_existing_account_moves(account_move_date, "commuting")

            employees_with_commuting = employees.filtered("carbon_commuting_ids")
            decimal_precision = self.env["decimal.precision"].precision_get(
                "Carbon value"
            )

            company_commuting_carbon_value = 0
            company_commuting_km = 0
            aml_vals_list = []

            for employee in employees_with_commuting:
                aml_vals = employee._get_carbon_commuting_line_vals(account_move_date)
                company_commuting_carbon_value += aml_vals.get("carbon_debt")
                company_commuting_km += sum(
                    employee.carbon_commuting_ids.mapped("distance_km")
                    * WEEKS_PER_MONTH
                )
                aml_vals_list.append((0, 0, aml_vals))

            average_carbon_per_km = self.calculate_average(
                company_commuting_carbon_value, company_commuting_km
            )

            for employee in employees - employees_with_commuting:
                if employee.km_home_work:
                    commuting_carbon = (
                        employee.km_home_work
                        * 10
                        * average_carbon_per_km
                        * WEEKS_PER_MONTH
                    )
                    commuting_details = f"\n| {employee.km_home_work * 10} Km"
                else:
                    commuting_carbon = self.calculate_average(
                        company_commuting_carbon_value, len(employees_with_commuting)
                    )
                    commuting_details = f"\n| {round(commuting_carbon, decimal_precision)} -> Company average emission for commuting"

                aml_vals = employee._get_carbon_commuting_line_vals(account_move_date)
                aml_vals.update(
                    {
                        "carbon_debt": commuting_carbon,
                        "name": f"{employee.name}{commuting_details}",
                        "carbon_origin_json": {
                            "mode": "manual",
                            "details": {
                                "uid": self.env.uid,
                                "username": self.env.user.name,
                            },
                        },
                    }
                )
                aml_vals_list.append((0, 0, aml_vals))

            ref = f'Employee_Commuting_Carbon_{account_move_date.strftime("%Y%m")}'
            journal_id = self.employee_commuting_journal_id.id
            account_move = self.create_account_move(
                ref,
                journal_id,
                account_move_date,
                aml_vals_list,
                "commuting",
            )

            if to_post:
                account_move.action_post()

            return True

        except Exception as e:
            _logger.error(f"Error processing commuting carbon emissions: {e}")
            return False

    def remote_work_create_account_move(self, account_move_date, to_post=False):
        """
        Generate account move for employee remote work carbon emissions.
        Calculates carbon emissions based on remote work days for each employee,
        fallback to average if no employees with remote work set.
        """
        self.ensure_one()

        try:
            employees = self.get_employees_with_contracts([("has_location", "=", True)])
            if not employees:
                _logger.info(
                    f"No employees found working from home for company {self.name}."
                )
                return False

            # Erase existing account moves for this date to avoid duplicates
            self.delete_existing_account_moves(account_move_date, "remote_work")

            total_home_working_days = sum(employees.mapped("work_days_home"))
            average_remote_work_days = self.calculate_average(
                total_home_working_days, len(employees)
            )

            aml_vals_list = []
            carbon_factor = self.employee_remote_work_carbon_factor_id.carbon_value

            for employee in employees:
                remote_work_days = employee.work_days_home
                remote_work_carbon = remote_work_days * carbon_factor * WEEKS_PER_MONTH

                aml_vals = self.prepare_account_move_line(
                    employee,
                    remote_work_carbon,
                    self.employee_remote_work_account_id.id,
                    f"{employee.name} Remote Work Carbon",
                )
                aml_vals_list.append((0, 0, aml_vals))

            # Handle average
            for employee in self.get_employees_with_contracts(
                [
                    ("work_days_home", "=", 0),
                    ("has_location", "=", False),
                ]
            ):
                remote_work_carbon = (
                    average_remote_work_days * carbon_factor * WEEKS_PER_MONTH
                )
                aml_vals = self.prepare_account_move_line(
                    employee,
                    remote_work_carbon,
                    self.employee_remote_work_account_id.id,
                    f"{employee.name} Remote Work Carbon (Company Average)",
                )
                aml_vals_list.append((0, 0, aml_vals))

            ref = f'Employee_Remote_Work_Carbon_{account_move_date.strftime("%Y%m")}'
            journal_id = self.employee_remote_work_journal_id.id
            account_move = self.create_account_move(
                ref,
                journal_id,
                account_move_date,
                aml_vals_list,
                "remote_work",
            )

            if to_post:
                account_move.action_post()

            _logger.info(f"Created account move: {account_move}")
            return True

        except Exception as e:
            _logger.error(f"Error processing remote work carbon emissions: {e}")
            return False
