import logging
from typing import Any

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CarbonCommonMixin(models.AbstractModel):
    _name = "carbon.common.mixin"
    _description = "Common Mixin for Shared Methods and Utils Fields"
    _carbon_enable_button = True

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

    # Carbon Line Origin Smart Button
    # In order to use this feature, you need to create this field in the model with an correct inverse_name.
    # carbon_line_origin_ids = fields.One2many(
    #     comodel_name="carbon.line.origin",
    #     inverse_name="<inverse_name in carbon.line.origin>",
    #     string="Origins",
    # )
    carbon_line_origin_qty = fields.Integer(compute="_compute_carbon_line_origin_qty")

    def action_see_carbon_line_origin_ids(self):
        return self._generate_action(
            model="carbon.line.origin",
            ids=self._get_carbon_line_origin_ids(),
        )

    def _compute_carbon_line_origin_qty(self):
        for record in self:
            record.carbon_line_origin_qty = len(record._get_carbon_line_origin_ids())

    def _get_carbon_line_origin_ids(self):
        return self.carbon_line_origin_ids.ids or []

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

    # View management system
    @api.model
    def _carbon_get_button_list(cls) -> list[dict[str, Any]]:
        """
        Return a list of buttons to add to the view. The buttons are dict that contains:
        - field: the field to display the value of the button. This shall contain the field name related to the qty field.
        - icon: the icon to display on the button. Not required, default is "fa-leaf"
        - action: the action to execute when the button is clicked. If not provided, this will be computed using the field name with .replace("_qty", "_ids") and prefixing it with "action_see_"
        - string: the string to display on the button
        You can also add as much key value pairs as you want, they will be added to the button as attributes.

        We will check if the field exists on the model, and if it doesn't, we will not add the button to the list.
        """
        button_list = [
            # Carbon origin button
            dict(
                field="carbon_line_origin_qty",
                icon="fa-leaf",
                # action="action_see_carbon_line_origin_ids",
                string=_("Carbon Footprint"),
                # invisible=False, # Always show the button
            ),
        ]

        return button_list

    @api.model
    def _get_view(cls, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
            if cls._carbon_enable_button:
                for button_box in arch.xpath("//div[@name='button_box']"):
                    button_box.extend(cls._carbon_generate_button_xml())

        return arch, view

    @api.model
    def _carbon_generate_button_xml(cls, model_name: str | None = None):
        model_name = model_name or cls._name
        if model_name not in cls.env:
            raise UserError(_("Model %s not found", model_name))
        model = cls.env[model_name]

        button_list = model._carbon_get_button_list()
        field_name_to_button = {}

        button_required_fields = ["field", "string"]
        for button_dict in button_list:
            if any(field not in button_dict for field in button_required_fields):
                raise UserError(_("Button %s is missing required fields", button_dict))

            field = button_dict.pop("field")
            if field not in model._fields:
                continue
            if field in field_name_to_button:
                raise UserError(_("Field %s is used by multiple buttons", field))

            button = etree.Element("button", name=f"sustainability_button_{field}")
            button.set("icon", button_dict.pop("icon", "fa-leaf"))
            button.set("type", "object")
            button.set("invisible", f"{field} < 1")
            button.set("class", f"oe_stat_button {button_dict.pop('class', '')}")

            for key, value in button_dict.items():
                button.set(key, str(value))

            field_name_to_button[field] = button

            action_method_name = f"action_see_{field.replace('_qty', '_ids')}"
            if button_dict.get("action"):
                button.set("name", button_dict.pop("action"))
            elif hasattr(model, action_method_name):
                button.set("name", action_method_name)
            else:
                _logger.warning(
                    f"Action {action_method_name} not found on model {model_name}"
                )
                continue

            div = etree.SubElement(
                button, "div", **{"class": "o_field_widget o_stat_info"}
            )
            span = etree.SubElement(div, "span", **{"class": "o_stat_value"})
            etree.SubElement(
                span, "field", **{"name": field, "nolabel": "1", "widget": "statinfo"}
            )
            span = etree.SubElement(div, "span", **{"class": "o_stat_text"})
            span.text = button_dict.pop("string")

        return list(field_name_to_button.values())
