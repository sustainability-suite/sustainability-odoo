from odoo import _, api, models


class CopyMixin(models.AbstractModel):
    _name = "carbon.copy.mixin"
    _description = "Mixin that allow to copy records with a new name"

    def _get_copy_name(self):
        self.ensure_one()
        fname = self._rec_name
        if fname in self._fields:
            new_name = self[fname]
        else:
            new_name = f"{self._name},{self.id}"
        return _("%s (copy)", new_name)

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        name = self._rec_name
        if name not in default:
            default[name] = self._get_copy_name()
        return super().copy(default=default)
