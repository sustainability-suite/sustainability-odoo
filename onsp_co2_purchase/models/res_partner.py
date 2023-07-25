from odoo import fields, models, api

class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "carbon.mixin"]

    @api.model
    def _get_available_carbon_compute_methods(self):
        return [
            ('monetary', 'Monetary'),
        ]

    carbon_in_compute_method = fields.Selection(default='monetary', selection=_get_available_carbon_compute_methods)

    def _get_carbon_in_value_fallback_records(self) -> list:
        self.ensure_one()
        res = super(ResPartner, self)._get_carbon_in_value_fallback_records()
        return res + [self.parent_id]

    def _get_carbon_out_value_fallback_records(self) -> list:
        self.ensure_one()
        res = super(ResPartner, self)._get_carbon_out_value_fallback_records()
        return res + [self.parent_id]

    @api.depends(
        'parent_id.carbon_in_value',
        'parent_id.carbon_in_compute_method',
        'parent_id.carbon_in_uom_id',
        'parent_id.carbon_in_monetary_currency_id',
    )
    def _compute_carbon_in_mode(self):
        super(ResPartner, self)._compute_carbon_in_mode()

    @api.depends(
        'parent_id.carbon_out_value',
        'parent_id.carbon_out_compute_method',
        'parent_id.carbon_out_uom_id',
        'parent_id.carbon_out_monetary_currency_id',
    )
    def _compute_carbon_out_mode(self):
        super(ResPartner, self)._compute_carbon_out_mode()


