from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CopyMixin(models.Model):
    _name = "carbon.copy.mixin"
    
    # --------------------------------------------
    #                   COPY
    # --------------------------------------------
    
    def _get_copy_name(self):
        self.ensure_one()
        return _("%s (copy)", self.name)
    
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = self._get_copy_name()
        return super().copy(default=default)
