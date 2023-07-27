from odoo import api, fields, models, _
from typing import Union


STATES_TO_AUTO_RECOMPUTE = ['draft', 'sent']

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    carbon_currency_id = fields.Many2one(related="order_id.carbon_currency_id")
    carbon_debt = fields.Monetary(
        string="CO2 Debt",
        currency_field="carbon_currency_id",
        help="A positive value means that your system's debt grows, a negative value means it shrinks",
        compute="_compute_carbon_debt",
        readonly=False,
        store=True,
    )
    carbon_value_origin = fields.Char(compute="_compute_carbon_debt", string="CO2e value origin", store=True)
    carbon_is_locked = fields.Boolean(default=False)

    @api.depends('product_id.carbon_in_value', 'product_qty')
    def _compute_carbon_debt(self):
        for line in self:
            line.carbon_debt = line.product_qty * line.product_id.carbon_in_value



    def action_recompute_carbon(self) -> dict:
        """ Force re-computation of carbon values for lines. Todo: add a confirm dialog if a subset is 'posted' """
        for line in self:
            line._compute_carbon_debt(force_compute='done')
        return {}

    def action_switch_locked(self):
        for line in self:
            line.carbon_is_locked = not line.carbon_is_locked


    @api.depends(
        'product_id.carbon_in_value',
        'product_id.carbon_in_compute_method',
        'product_id.carbon_in_uom_id',
        'product_id.carbon_in_monetary_currency_id',

        'product_qty',
        'product_uom',
        'price_subtotal',
        'order_id.date_approve',
        'order_id.currency_id',
    )
    def _compute_carbon_debt(self, force_compute: Union[bool, str, list[str]] = None):
        if force_compute is None:
            force_compute = []
        elif isinstance(force_compute, bool):
            force_compute = ['done', 'locked'] if force_compute else []
        elif isinstance(force_compute, str):
            force_compute = [force_compute]

        if 'done' not in force_compute:
            self = self.filtered(lambda l: l.order_id.state in STATES_TO_AUTO_RECOMPUTE)
        if 'locked' not in force_compute:
            self = self.filtered(lambda l: not l.carbon_is_locked)



        for line in self:
            # These are the common arguments for the carbon value computation
            # Others values are added below depending on the record type
            kw_arguments = {
                'carbon_type': 'in',
                'date': line.order_id.date_approve,
                'amount': line.price_subtotal,
                'from_currency_id': line.order_id.currency_id,
            }

            # Todo: make a call to `can_use_product_carbon_value()` defined in a "line mixin"
            if self.product_id and self.product_id.has_valid_carbon_in_value():
                record = line.product_id
                kw_arguments.update({
                    'quantity': line.product_qty,
                    'from_uom_id': line.product_uom,
                })
            else:
                record = line.order_id.company_id or self.env.company

            debt, infos = record.get_carbon_value(**kw_arguments)

            line.carbon_debt = debt
            line.carbon_value_origin = f"{infos['carbon_value_origin']}|{infos['carbon_value']}"





    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        res.update({
            'carbon_debt': self.qty_to_invoice * self.product_id.carbon_in_value,
            'carbon_is_locked': True,
            'carbon_value_origin': _("Purchase Order %s", self.order_id.name),
        })
        return res

