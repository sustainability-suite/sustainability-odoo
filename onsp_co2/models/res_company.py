from odoo import api, fields, models


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "carbon.mixin"]


    # For companies, carbon value is not linked to a factor and must be a plain value
    # -> We negate a lot of computation
    carbon_in_value = fields.Float(compute=False, store=True, readonly=False, tracking=True)
    carbon_out_value = fields.Float(compute=False, store=True, readonly=False, tracking=True)
    carbon_in_value_origin = fields.Char(compute=False, store=True, related="name")
    carbon_out_value_origin = fields.Char(compute=False, store=True, related="name")
    carbon_in_monetary_currency_id = fields.Many2one(compute="_compute_carbon_currencies", store=True, string="CO2e Currency for 'in' moves")
    carbon_out_monetary_currency_id = fields.Many2one(compute="_compute_carbon_currencies", store=True, string="CO2e Currency for 'out' moves")
    carbon_in_compute_method = fields.Selection(selection=[('monetary', 'Monetary')], default='monetary', required=True)
    carbon_out_compute_method = fields.Selection(selection=[('monetary', 'Monetary')], default='monetary', required=True)

    invoice_report_footer = fields.Html(translate=True)
    carbon_lock_date = fields.Date(
        string="CO2e Computation Lock Date",
        tracking=True,
        help="",
    )


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['carbon_in_is_manual'] = True
            vals['carbon_out_is_manual'] = True
        return super(ResCompany, self).create(vals_list)

    # Monkey patch to avoid ValidationError that would lead to incomplete fields
    def _check_mandatory_fields(self):
        pass

    @api.depends('currency_id')
    def _compute_carbon_currencies(self):
        for company in self:
            company.carbon_in_monetary_currency_id = company.currency_id
            company.carbon_out_monetary_currency_id = company.currency_id
