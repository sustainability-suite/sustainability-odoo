from odoo import _, api, models


class CarbonLineMixin(models.AbstractModel):
    _inherit = "carbon.line.mixin"

    @api.model
    def _get_computation_levels_mapping(self) -> dict:
        mapping = super()._get_computation_levels_mapping()
        mapping["stock.picking"] = _("Freight transport")
        return mapping
