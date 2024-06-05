from odoo import _, models


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
