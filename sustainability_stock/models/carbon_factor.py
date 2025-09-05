from lxml import etree

from odoo import api, fields, models


class CarbonFactor(models.Model):
    _inherit = "carbon.factor"

    is_climatiq = fields.Boolean(default=False)

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        """
        This method is used to make the form readonly when is_climatiq is True.
        And add the is_climatiq field in the comment group.
        """
        IGNORE_FIELDS = [
            "is_climatiq",
            "root",
            "category",
            "carbon_value",
            "carbon_currency_label",
            "unit_label",
        ]
        IGNORE_FIELDS_ENDSWITH = ["_qty"]
        IGNORE_PARENT_TAGS = ["list", "form"]
        READONLY_CLIMATIQ = "is_climatiq"

        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
            if comment_group_node := arch.xpath("//field[@name='comment']/.."):
                comment_group_node[0].append(
                    etree.Element(
                        "field",
                        {
                            "name": "is_climatiq",
                            "widget": "boolean_toggle",
                            "readonly": "1",
                            "invisible": "not is_climatiq",
                        },
                    )
                )

            for field in arch.iter("field"):
                if parent := field.xpath(".."):
                    if parent[0].tag in IGNORE_PARENT_TAGS:
                        continue
                if field.get("name") in IGNORE_FIELDS:
                    continue
                if any(
                    field.get("name").endswith(suffix)
                    for suffix in IGNORE_FIELDS_ENDSWITH
                ):
                    continue
                if readonly := field.get("readonly"):
                    field.set("readonly", f"{READONLY_CLIMATIQ} or ({readonly})")
                    continue
                field.set("readonly", f"{READONLY_CLIMATIQ}")
        return arch, view
