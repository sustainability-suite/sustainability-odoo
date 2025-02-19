from odoo import _, api, fields, models


class CarbonCommonMixin(models.AbstractModel):
    _name = "carbon.common.mixin"
    _description = "Common Mixin for Shared Methods and Utils Fields"

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

    # Carbon Origin Child Smart Button
    carbon_origin_child_ids = fields.One2many(
        comodel_name="carbon.line.origin", compute="_compute_carbon_origin_child_ids"
    )
    carbon_origin_child_qty = fields.Integer(compute="_compute_carbon_origin_child_qty")

    @api.model
    def _carbon_get_line_field(cls):
        """
        This field is used to display the carbon.line.origin from the child field smart button.
        If you don't want the feature don't override this method, so it will raise an error if you try to use it.

        Returns:
            str: The name of the field that contains the carbon.line.origin records.
        """
        raise NotImplementedError(
            f"Method _carbon_get_line_field not implemented in {cls._name}"
        )

    def _compute_carbon_origin_child_ids(self):
        """
        Compute the carbon.line.origin records through the child field for smart button usually.
        """
        line_field = self._carbon_get_line_field()
        for record in self:
            record.carbon_origin_child_ids = record[line_field].mapped(
                "carbon_origin_ids"
            )

    @api.depends("carbon_origin_child_ids")
    def _compute_carbon_origin_child_qty(self):
        """
        Compute the quantity of carbon.line.origin records through the child field for smart button usually.
        """
        for record in self:
            record.carbon_origin_child_qty = len(record.carbon_origin_child_ids)

    def action_see_clo_child_ids(self):
        """
        Open a new window to display the carbon.line.origin records from the child field for smart button.
        """
        return self._generate_action(
            title=_("Carbon Footprint"),
            model="carbon.line.origin",
            ids=self.carbon_origin_child_ids.ids,
        )
