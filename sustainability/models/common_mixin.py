from odoo import _, api, models
from odoo.exceptions import AccessError


class CommonMixin(models.AbstractModel):
    _name = "common.mixin"
    _description = "Common Mixin for Shared Methods"

    def _generate_action(self, model: str, title: str, ids: list[int]) -> dict:
        """
        Generate an action dictionary for the specified model and title.

        This function creates an action dictionary that can be used to open a new window in the Odoo UI. The new window will display the specified model's data, filtered by the carbon domain.

        Args:
            model (str): The name of the model to display in the new window.
            title (str): The title to display in the new window.
            ids (list[int]): A list of integer IDs representing the records to be displayed in the new window.

        Returns:
            dict: An action dictionary that can be used to open a new window in the Odoo UI.
        """
        self.ensure_one()
        return {
            "name": _("%s %s", title, self.name),
            "type": "ir.actions.act_window",
            "res_model": model,
            "views": [(False, "tree"), (False, "form")],
            "domain": [("id", "in", ids)],
            "target": "current",
            "context": {
                **self.env.context,
            },
        }

    @api.model
    def _CARBON_FIELD_PREFIX(cls):
        return "carbon_"

    @api.model
    def _get_carbon_fields_name(cls, fields=None):
        if not fields:
            fields = []
        carbon_fields = []
        for field in cls._fields:
            if field.startswith(cls._CARBON_FIELD_PREFIX()):
                carbon_fields.append(field)
        for field in fields:
            if field not in cls._fields.keys():
                continue
            carbon_fields.append(field)
        return carbon_fields

    @api.model
    def _get_carbon_fields_custom_group(
        cls
    ):  # TODO: Add a OR option, so we can add multiple groups and it will be (sustainability_admin and (group1 or group2)). Add a check if group exist so no error raised but a warning.
        """
        This method allow to choose an custom group for the carbon fields. This is in addition to the default sustainability admin group.
        Should be overridden in the model.
        Can be false if no custom group is needed.
        Can be multiple groups separated by comma.
        """
        return False

    @api.model
    def _get_carbon_fields_groups(self):
        admin_group = "sustainability.group_sustainability_admin"
        custom_group = self._get_carbon_fields_custom_group()
        return admin_group if not custom_group else f"{admin_group},{custom_group}"

    def write(self, vals):
        res = super().write(vals)
        carbon_fields = self._get_carbon_fields_name()
        carbon_groups = self._get_carbon_fields_groups()
        if self.env.context.get("install_mode", False) or self.env.is_system():
            return res
        for field in vals.keys():
            if field in carbon_fields:
                if not self.env.user.user_has_groups(carbon_groups):
                    raise AccessError(
                        _(
                            f"You are not allowed to modify carbon fields. Please contact your administrator. (model: {self._name}, field: {field}, user: {self.env.user.name})"
                        )
                    )
        return res
