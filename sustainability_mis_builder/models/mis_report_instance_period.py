from odoo import models


class InstPeriodCO2(models.Model):
    _inherit = "mis.report.instance.period"

    def _get_additional_move_line_filter(self):
        domain = super()._get_additional_move_line_filter()

        # Todo: check if there is a better way to do this, as this got refactored a lot in v16
        # the super now uses _get_filter_domain()
        if self.source_aml_model_name == "mis.co2.account.move.line":
            domain.extend([("move_id.state", "!=", "cancel")])

            if self.report_instance_id.target_move == "posted":
                domain.extend([("move_id.state", "=", "posted")])

        return domain
