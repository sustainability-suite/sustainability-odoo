from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class CarbonLineOrigin(models.Model):
    _name = "carbon.line.origin"
    _description = "carbon.line.origin"

    # Fake Many2one that is used in the One2many field in `carbon.line.mixin`
    res_model_id = fields.Many2one('ir.model', index=True, ondelete='cascade', required=True)
    res_model = fields.Char(related='res_model_id.model', index=True, precompute=True, store=True, readonly=True, string="Model")
    res_id = fields.Many2oneReference(index=True, model_field='res_model', string="ID")

    factor_value_id = fields.Many2one('carbon.factor.value', string="Factor value")
    factor_value_type_id = fields.Many2one(related='factor_value_id.type_id', string="Factor Value Type")
    factor_id = fields.Many2one(related='factor_value_id.factor_id', string="Carbon Factor", store=True)

    value = fields.Float(digits="Carbon value")          # Result of the computation (might be a partial result)
    distribution = fields.Float()
    carbon_value = fields.Float(digits="Carbon Factor value")
    uncertainty_percentage = fields.Float(default=0.0)
    uncertainty_value = fields.Float(default=0.0, digits="Carbon Factor value")
    compute_method = fields.Char()
    uom_id = fields.Many2one('uom.uom')
    monetary_currency_id = fields.Many2one('res.currency')

    comment = fields.Char(string="Comment")



    @api.model
    def _get_model_to_field_name(self) -> dict[str, str]:
        return {
            'account.move.line': 'move_line_id',
        }

    """
    Real many2one fields that are computed from the fake Many2one
    Other fields are in submodules:
    - onsp_co2_purchase: purchase_line_id
    - onsp_co2_hr_expense_report: expense_id
    - etc...
    
    These are useful to create related fields!
    """
    move_line_id = fields.Many2one('account.move.line', compute="_compute_many2one_lines", store=True, string="Move Line")
    move_id = fields.Many2one(related="move_line_id.move_id", store=True, string="Move")
    account_id = fields.Many2one(related="move_line_id.account_id", store=True, string="Account")



    @api.depends('res_model', 'res_id')
    def _compute_many2one_lines(self):
        """ Update the corresponding many2one field on the line """
        model_to_field_name = self._get_model_to_field_name()
        default_vals = {field_name: False for field_name in model_to_field_name.values()}

        for origin in self:
            vals = {**default_vals}
            if origin.res_model in model_to_field_name:
                vals[model_to_field_name[origin.res_model]] = origin.res_id
            origin.update(vals)

    @api.model
    def _clean_orphan_lines(self):
        """
        Extra-cleaning method to remove lines that have no origin
        Mid-term goal is to deprecate it/remove it. The logger is here to help us doing this decision.
        """
        lines_to_remove = self.search([('res_id', 'in', [0, False])])
        if lines_to_remove:
            _logger.warning("CarbonLineOrigin: %s lines will be removed because they have no origin", len(lines_to_remove))
            lines_to_remove.unlink()

    @api.model_create_multi
    def create(self, vals_list):
        res = super(CarbonLineOrigin, self).create(vals_list)
        self._clean_orphan_lines()
        return res



