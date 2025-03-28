from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase


class CarbonCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Disable tracking test suite
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)

        # Clean up demo data in order to test specific case
        moves = cls.env["account.move"].search([("state", "=", "posted")])
        moves.button_draft()
        moves.unlink()
        cls.env["hr.employee"].search([]).write({"active": False})

        cls.uom_km = cls.env.ref("uom.product_uom_km")
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.currency_usd = cls.env.ref("base.USD")

        cls.carbon_factor_transportation = cls.env["carbon.factor"].create(
            {"name": "Transportation Factor"}
        )
        cls.carbon_factor_bicycle = cls.env["carbon.factor"].create(
            {
                "name": "Bicycle Factor",
                "carbon_compute_method": "physical",
                "parent_id": cls.carbon_factor_transportation.id,
            }
        )
        cls.carbon_factor_remote_work = cls.env["carbon.factor"].create(
            {
                "name": "Remote Work Factor",
                "carbon_compute_method": "physical",
            }
        )
        cls.env["carbon.factor.value"].create(
            [
                {
                    "factor_id": cls.carbon_factor_bicycle.id,
                    "carbon_uom_id": cls.uom_km.id,
                    "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                    "carbon_value": 0.01,
                },
                {
                    "factor_id": cls.carbon_factor_remote_work.id,
                    "carbon_uom_id": cls.uom_day.id,
                    "date": datetime.today().strftime("%Y-%m-%d %H:%M"),
                    "carbon_value": 1,
                },
            ]
        )

        cls.carbon_journal = cls.env["account.journal"].create(
            {
                "name": "Carbon",
                "code": "CO2TEST",
                "type": "purchase",
                "company_id": cls.env.company.id,
                "currency_id": cls.currency_usd.id,
            }
        )
        cls.carbon_account = cls.env["account.account"].create(
            {
                "name": "Carbon extra-accounting",
                "code": "10001",
                "account_type": "expense",
                "company_ids": [(6, 0, [cls.env.company.id])],
            }
        )

        cls.env.company.write(
            {
                "employee_commuting_carbon_factor_id": cls.carbon_factor_transportation.id,
                "employee_commuting_journal_id": cls.carbon_journal.id,
                "employee_commuting_account_id": cls.carbon_account.id,
                "employee_commuting_carbon_cronjob_active": True,
                "employee_remote_work_carbon_factor_id": cls.carbon_factor_remote_work.id,
                "employee_remote_work_journal_id": cls.carbon_journal.id,
                "employee_remote_work_account_id": cls.carbon_account.id,
                "employee_remote_work_carbon_cronjob_active": True,
                "carbon_lock_date": (
                    datetime.today() - relativedelta(months=6)
                ).strftime("%Y-%m-%d"),
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Home Address",
                "street": "123 Remote St",
                "city": "Remote City",
                "country_id": cls.env.ref("base.us").id,
            }
        )
        cls.home_location, cls.office_location = cls.env["hr.work.location"].create(
            [
                {"name": "Home", "location_type": "home", "address_id": cls.partner.id},
                {
                    "name": "Office",
                    "location_type": "office",
                    "address_id": cls.partner.id,
                },
            ]
        )

        (
            cls.employee_home,
            cls.employee_office,
            cls.employee_no_location,
            cls.employee_new_contract,
            cls.employee_no_contract,
        ) = cls.env["hr.employee"].create(
            [
                {
                    "name": "Test Employee Home",
                    "company_id": cls.env.company.id,
                    "monday_location_id": cls.home_location.id,
                },
                {
                    "name": "Test Employee Office",
                    "company_id": cls.env.company.id,
                    "tuesday_location_id": cls.office_location.id,
                },
                {"name": "Test Employee No Location", "company_id": cls.env.company.id},
                {
                    "name": "Test Employee New Contract",
                    "company_id": cls.env.company.id,
                    "monday_location_id": cls.home_location.id,
                    "tuesday_location_id": cls.office_location.id,
                },
                {
                    "name": "Test Employee No Contract",
                    "company_id": cls.env.company.id,
                },
            ]
        )
        cls.env["hr.contract"].create(
            [
                {
                    "name": "Test Contract",
                    "employee_id": emp.id,
                    "date_start": datetime(datetime.today().year - 1, 1, 1).strftime(
                        "%Y-%m-%d"
                    ),  # First day of last year
                    "state": "open",
                    "wage": 3000,
                    "company_id": cls.env.company.id,
                }
                for emp in (
                    cls.employee_home,
                    cls.employee_office,
                    cls.employee_no_location,
                )
            ]
        )
        cls.env["hr.contract"].create(
            {
                "name": "Test Contract 3 months ago",
                "employee_id": cls.employee_new_contract.id,
                "date_start": (datetime.today() - relativedelta(months=3)).strftime(
                    "%Y-%m-%d"
                ),
                "state": "open",
                "wage": 3000,
                "company_id": cls.env.company.id,
            }
        )

        cls.env["carbon.hr.commuting"].create(
            {
                "carbon_factor_id": cls.carbon_factor_bicycle.id,
                "distance_km": 40,
                "employee_id": cls.employee_home.id,
            }
        )
