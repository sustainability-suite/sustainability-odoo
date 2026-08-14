# © 2023 Open Net Sarl
from odoo.addons.sustainability.hooks import add_fields, carbon_mixin_fields_spec

from . import models


def pre_init_hook(env):
    """Pre_init_hook to avoid performance issues on large databases.

    See sustainability.hooks.add_fields for the rationale.
    """
    add_fields(
        env,
        carbon_mixin_fields_spec(
            [("hr.expense", "carbon.line.mixin")],
            "sustainability_hr_expense_report",
        ),
    )
