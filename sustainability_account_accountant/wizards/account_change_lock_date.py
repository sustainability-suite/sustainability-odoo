import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AccountChangeLockDate(models.TransientModel):
    _inherit = "account.change.lock.date"

    carbon_lock_date = fields.Date(
        string="CO2e Computation Lock Date",
        default=lambda self: self.env.company.carbon_lock_date,
        help="Prevents CO2e computation on entries prior to the defined date.",
    )

    def _prepare_lock_date_values(self):
        res = super()._prepare_lock_date_values()
        res.update({"carbon_lock_date": self.carbon_lock_date})
        return res
