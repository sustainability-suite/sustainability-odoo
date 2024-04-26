from typing import Dict

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ConfirmDialog(models.TransientModel):
    _name = "confirm.dialog"

    ALLOWED_METHODS_BY_MODEL: Dict[str, list] = {
        "account.move": ["action_recompute_carbon"]
    }

    ALLOWED_METHODS_ACROSS_MODEL: list = ["copy"]

    message = fields.Char(
        required=True, readonly=True, default="Are you sure you want to continue ?"
    )
    callback = fields.Char(required=True, readonly=True)
    res_model = fields.Char(required=True, readonly=True)
    # res_ids is a simple ",".join(self.ids)
    res_ids = fields.Char(required=True, readonly=True)

    def action_confirm(self):
        self.ensure_one()
        if self.res_model not in self.env:
            raise ValidationError(_("The model %s doesn't exist.", self.res_model))

        records = self.env[self.res_model].browse(
            [int(id) for id in self.res_ids.split(",")]
        )

        f = getattr(records, self.callback)
        if not f:
            raise ValidationError(
                _(
                    "The model %s doesn't have a method named %s.",
                    self.res_model,
                    self.callback,
                )
            )
        if (
            f.__name__ in self.ALLOWED_METHODS_ACROSS_MODEL
            or f.__name__ in self.ALLOWED_METHODS_BY_MODEL.get(self.res_model)
        ):
            f()
        else:
            raise ValidationError(
                _(
                    "The method '%s' on model '%s' aren't allow to be called using the confirm dialog",
                    self.callback,
                    self.res_model,
                )
            )

        return {}

    def get_action(self):
        if self.user_has_groups("onsp_co2.skip_warning"):
            self.action_recompute_carbon()
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
