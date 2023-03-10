from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    carbon_value = fields.Float(
        related='company_id.carbon_value',
        readonly=False,
    )
    carbon_sale_value = fields.Float(
        related='company_id.carbon_sale_value',
        readonly=False,
    )

    invoice_report_footer = fields.Html(
        related='company_id.invoice_report_footer',
        readonly=False
    )

