import logging
import time

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "carbon.mixin", "carbon.common.mixin"]

    @api.model
    def _get_available_carbon_compute_methods(self):
        return [
            ("monetary", "Monetary"),
        ]

    carbon_in_mode = fields.Selection(recursive=True)
    carbon_out_mode = fields.Selection(recursive=True)
    has_computed_carbon_mode = fields.Boolean(default=False)
    carbon_line_origin_ids = fields.One2many(
        comodel_name="carbon.line.origin",
        inverse_name="move_line_partner_id",
        string="Origins",
    )
    carbon_line_origin_qty = fields.Integer(compute="_compute_carbon_line_origin_qty")

    def _get_carbon_in_fallback_records(self) -> list:
        self.ensure_one()
        res = super()._get_carbon_in_fallback_records()
        return res + [self.parent_id]

    def _get_carbon_out_fallback_records(self) -> list:
        self.ensure_one()
        res = super()._get_carbon_out_fallback_records()
        return res + [self.parent_id]

    @api.depends("parent_id.carbon_in_factor_id")
    def _compute_carbon_in_mode(self):
        return super()._compute_carbon_in_mode()

    @api.depends("parent_id.carbon_out_factor_id")
    def _compute_carbon_out_mode(self):
        return super()._compute_carbon_out_mode()

    def _cron_initial_carbon_compute_res_partner(self):
        partners = self.env["res.partner"].search(
            [("has_computed_carbon_mode", "=", False)]
        )

        if not partners:
            cron_id = self.env.ref(
                "sustainability_purchase.cron_initial_carbon_compute_res_partner"
            )
            _logger.warning(
                f"Please deactivate cron '{cron_id.name}' as it is not needed anymore."
            )
            return

        clock = time.perf_counter()
        total = 0
        _logger.info(
            f"Running _cron_initial_carbon_compute_res_partner on {len(partners)} records"
        )

        for partner in partners:
            if time.perf_counter() - clock >= 270:
                break
            try:
                with self.env.cr.savepoint():
                    # Create a savepoint and rollback this section if any exception is raised.
                    partner._compute_carbon_in_mode()
                    partner._compute_carbon_out_mode()
                    partner.write({"has_computed_carbon_mode": True})
                    total += 1
            # Catch here any exceptions if you need to.
            except Exception as e:
                _logger.error(
                    f"Error on cron _cron_initial_carbon_compute_res_partner : Exception: {e}"
                )

        _logger.info(
            f"_cron_initial_carbon_compute_res_partner finished for {total} partners ({len(partners) - total} remaining)"
        )

    def action_see_carbon_line_origin_ids(self):
        return self._generate_action(
            model="carbon.line.origin",
            ids=self.carbon_line_origin_ids.ids,
        )

    def _compute_carbon_line_origin_qty(self):
        for factor in self:
            factor.carbon_line_origin_qty = len(factor.carbon_line_origin_ids)
