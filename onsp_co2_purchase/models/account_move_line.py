from odoo import api, fields, models



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    move_partner_id = fields.Many2one(related="move_id.partner_id", store=True)

    @api.model
    def get_possible_fields_to_compute_carbon(self):
        res = super(AccountMoveLine, self).get_possible_fields_to_compute_carbon()
        prod_index = res.index('product_id')
        res = res[:prod_index+1] + ['partner_id', 'move_partner_id'] + res[prod_index+1:]
        return res

    # --- Partner ---
    def can_use_partner_id_carbon_value(self) -> bool:
        self.ensure_one()
        return self.partner_id and self.partner_id.has_valid_carbon_in_value()

    # --- Move Partner ---
    def can_use_move_partner_id_carbon_value(self) -> bool:
        self.ensure_one()
        return self.move_partner_id and self.move_partner_id.has_valid_carbon_in_value()

    @api.depends(
        'partner_id.carbon_in_value',
        'partner_id.carbon_in_compute_method',
        'partner_id.carbon_in_uom_id',
        'partner_id.carbon_in_monetary_currency_id',

        'move_partner_id.carbon_in_value',
        'move_partner_id.carbon_in_compute_method',
        'move_partner_id.carbon_in_uom_id',
        'move_partner_id.carbon_in_monetary_currency_id',
    )
    def _compute_carbon_debt(self, force_compute=None):
        return super(AccountMoveLine, self)._compute_carbon_debt(force_compute)

