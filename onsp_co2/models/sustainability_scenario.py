from odoo import _, fields, models


class SustainabilityScenario(models.Model):
    _name = "sustainability.scenario"
    _description = "Sustainability Scenario"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    description = fields.Text(required=True)
    end_date = fields.Date(required=True)
    active = fields.Boolean(default=True)

    action_plan_ids = fields.One2many("sustainability.action.plan", "scenario_id")
    action_plan_qty = fields.Integer(compute="_compute_action_plan_qty")
    action_qty = fields.Integer(compute="_compute_action_qty")

    def _compute_action_plan_qty(self):
        for scenario in self:
            scenario.action_plan_qty = len(scenario.action_plan_ids)

    def _compute_action_qty(self):
        for scenario in self:
            actions = self.env["sustainability.action"].search(
                [("action_plan_ids.scenario_id", "=", scenario.id)]
            )
            scenario.action_qty = len(actions)

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
            "name": _("%s %s", title, self.display_name),
            "type": "ir.actions.act_window",
            "res_model": model,
            "views": [(False, "tree"), (False, "form")],
            "domain": [("id", "in", ids)],
            "target": "current",
            "context": {
                **self.env.context,
            },
        }

    def _get_action_plan_ids(self):
        return (
            self.env["sustainability.action.plan"]
            .search([("scenario_id", "in", self.ids)])
            .ids
        )

    def action_see_action_plans(self):
        return self._generate_action(
            title=_("Action Plans for"),
            model="sustainability.action.plan",
            ids=self._get_action_plan_ids(),
        )

    def action_see_actions(self):
        action_ids = (
            self.env["sustainability.action"]
            .search([("action_plan_ids", "in", self._get_action_plan_ids())])
            .ids
        )
        return self._generate_action(
            title=_("Actions for"),
            model="sustainability.action",
            ids=action_ids,
        )
