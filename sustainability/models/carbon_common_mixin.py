from odoo import _, api, fields, models


class CarbonCommonMixin(models.AbstractModel):
    _name = "carbon.common.mixin"
    _description = "Common Mixin for Shared Methods and Utils Fields"

    def _generate_action(
        self,
        model: str,
        title: str = _("Carbon Footprint for"),
        ids: list[int] | None = None,
        domain: list | None = None,
    ) -> dict:
        """Generate an action dictionary for opening a new window in the Odoo UI."""
        self.ensure_one()

        ids = ids or []
        domain = domain or []

        if ids:
            domain = [("id", "in", ids)]

        return {
            "name": f"{title} {self.name}",
            "type": "ir.actions.act_window",
            "res_model": model,
            "views": [(False, "list"), (False, "form")],
            "domain": domain,
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
        If you don't want the feature don't override this method, so it will do nothing if you try to use it.
        If method do not return string, it will ignore the field.

        Returns:
            str: The name of the field that contains the carbon.line.origin records.
        """
        return False

    def _compute_carbon_origin_child_ids(self):
        """
        Compute the carbon.line.origin records through the child field for smart button usually.
        """
        line_field = self._carbon_get_line_field()
        for record in self:
            if not isinstance(line_field, str) or not line_field:
                record.carbon_origin_child_ids = self.env["carbon.line.origin"]
                continue
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
            model="carbon.line.origin",
            ids=self.carbon_origin_child_ids.ids,
        )
