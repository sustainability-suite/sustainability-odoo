from odoo import _, fields, models
from odoo.exceptions import ValidationError


class CarbonConfirmDialog(models.TransientModel):
    _name = "carbon.confirm.dialog"

    message = fields.Char(
        required=True, readonly=True, default="Are you sure you want to continue ?"
    )

    def action_confirm(self):
        model = self.env.context["model"]
        if model not in self.env:
            raise ValidationError(_("The model %s doesn't exist.", model))

        ids = self.env[model].browse(self.env.context["ids"])
        fname = self.env.context["fname"]

        f = getattr(ids, fname)
        if not f:
            raise ValidationError(
                _("The model %s doesn't have a function named %s.", model, fname)
            )

        f()

        return {}

    def action_cancel(self):
        return {}
