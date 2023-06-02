from odoo import api, fields, models


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "carbon.mixin"]

    @api.model
    def _get_available_carbon_compute_methods(self):
        return [
            ('monetary', 'Monetary'),
        ]

    # For companies, carbon value is not linked to a factor and must be a plain value
    # -> We negate a lot of computation
    carbon_in_value = fields.Float(compute=False, store=True, readonly=False, tracking=True)
    carbon_out_value = fields.Float(compute=False, store=True, readonly=False, tracking=True)
    carbon_in_value_origin = fields.Char(compute=False, store=True, related="name")
    carbon_out_value_origin = fields.Char(compute=False, store=True, related="name")
    carbon_in_monetary_currency_id = fields.Many2one(compute="_compute_carbon_currencies")
    carbon_out_monetary_currency_id = fields.Many2one(compute="_compute_carbon_currencies")
    carbon_in_compute_method = fields.Selection(default='monetary', required=True)
    carbon_out_compute_method = fields.Selection(default='monetary', required=True)

    invoice_report_footer = fields.Html(translate=True)


    @api.depends('currency_id')
    def _compute_carbon_currencies(self):
        for company in self:
            company.carbon_in_monetary_currency_id = company.currency_id
            company.carbon_out_monetary_currency_id = company.currency_id
