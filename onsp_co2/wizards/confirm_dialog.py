from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ConfirmDialog(models.TransientModel):
    _name = "confirm.dialog"

    message = fields.Char(
        required=True, readonly=True, default="Are you sure you want to continue ?"
    )
    callback = fields.Char(required=True, readonly=True)
    res_model = fields.Char(required=True, readonly=True)
    # res_ids is a simple ",".join(self.ids)
    res_ids = fields.Char(required=True, readonly=True)

    skip_group_ids = fields.Many2many(comodel_name="res.groups")

    def action_confirm(self):
        self.ensure_one()
        if self.res_model not in self.env:
            raise ValidationError(_("The model %s doesn't exist.", self.res_model))

        records = self.env[self.res_model].browse(
            [int(id) for id in self.res_ids.split(",")]
        )

        ALLOWED_METHODS = records._confirm_dialog_methods or []

        f = getattr(records, self.callback)
        if not f:
            raise ValidationError(
                _(
                    "The model %s doesn't have a method named %s.",
                    self.res_model,
                    self.callback,
                )
            )
        if f.__name__ in ALLOWED_METHODS:
            f()
        else:
            raise ValidationError(
                _(
                    "The method '%s' on model '%s' isn't allow to be called using the confirm dialog. You can authorize it using _confirm_dialog_methods.",
                    self.callback,
                    self.res_model,
                )
            )

        return {}

    def get_action(self):
        if self.env.user in self.skip_group_ids.users:
            self.action_confirm()
            return {}

        return {
            "name": "Warning",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "confirm.dialog",
            "res_id": self.id,
            "target": "new",
            "context": {
                **self.env.context,
            },
        }
