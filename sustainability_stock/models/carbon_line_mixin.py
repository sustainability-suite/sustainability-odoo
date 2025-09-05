from odoo import _, api, models


class CarbonLineMixin(models.AbstractModel):
    _inherit = "carbon.line.mixin"

    @api.model
    def _get_computation_levels_mapping(self) -> dict:
        mapping = super()._get_computation_levels_mapping()
        mapping["stock.picking"] = _("Freight transport")
        return mapping

    def _get_line_origin_vals_list(self):
        """
        Returns a list of values for the origin field based on the stock picking.
        """
        res = super()._get_line_origin_vals_list()
        model_name = self.carbon_origin_json.get("model_name", "")
        json_details = self.carbon_origin_json.get("details", {})
        if model_name == "stock.picking":
            for line in res:
                line["factor_id"] = json_details.get("factor_id", False)

        return res
