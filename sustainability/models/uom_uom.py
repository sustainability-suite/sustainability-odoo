from odoo import api, fields, models


class UomUom(models.Model):
    _inherit = "uom.uom"

    sustainability_is_physical = fields.Boolean(
        string="Is physical",
        compute="_compute_sustainability_is_physical",
        store=True,
        readonly=False,
    )

    @api.depends("relative_uom_id", "related_uom_ids")
    def _compute_sustainability_is_physical(self):
        physical_uom_kg = self.env.ref("uom.product_uom_kgm")
        physical_uom_lb = self.env.ref("uom.product_uom_lb")
        for uom in self:
            parents = uom.with_context(active_test=False).search(
                [("id", "parent_of", uom.id)]
            )
            childs = uom.with_context(active_test=False).search(
                [("id", "child_of", uom.id)]
            )
            if (
                physical_uom_kg.id in (parents | childs).ids
                or physical_uom_lb.id in (parents | childs).ids
            ):
                uom.sustainability_is_physical = True
            else:
                uom.sustainability_is_physical = False
