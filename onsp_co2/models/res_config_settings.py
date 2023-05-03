from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    carbon_in_value = fields.Float(
        related='company_id.carbon_in_value',
        readonly=False,
    )
    carbon_out_value = fields.Float(
        related='company_id.carbon_out_value',
        readonly=False,
    )
    invoice_report_footer = fields.Html(
        related='company_id.invoice_report_footer',
        readonly=False,
        translate=True,
    )

