import logging
import time

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "carbon.mixin"]

    @api.model
    def _get_available_carbon_compute_methods(self):
        return [
            ("monetary", "Monetary"),
        ]

    carbon_in_mode = fields.Selection(recursive=True)
    carbon_out_mode = fields.Selection(recursive=True)
    has_computed_carbon_mode = fields.Boolean(default=False)

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
                "Please deactivate cron '%s' as it is not needed anymore."
                % cron_id.name
            )
            return

        clock = time.perf_counter()
        total = 0
        _logger.info(
            "Running _cron_initial_carbon_compute_res_partner on %s records"
            % len(partners)
        )

        for partner in partners:
            if time.perf_counter() - clock >= 270:
                break
            try:
                partner._compute_carbon_in_mode()
                partner._compute_carbon_out_mode()
                partner.write({"has_computed_carbon_mode": True})
                self.env.cr.commit()
                total += 1

            except Exception as e:
                self.env.cr.rollback()
                _logger.error(
                    "Error on cron _cron_initial_carbon_compute_res_partner : Exception: %s"
                    % e
                )

        _logger.info(
            "_cron_initial_carbon_compute_res_partner finished for %s partners (%s remaining)"
            % (total, len(partners) - total)
        )
