from odoo import api, fields, models


class CarbonLineOrigin(models.Model):
    _inherit = "carbon.line.origin"

    sale_line_id = fields.Many2one(
        "sale.order.line",
        compute="_compute_many2one_lines",
        store=True,
        string="Sale Line",
    )

    @api.model
    def _get_model_to_field_name(self) -> dict[str, str]:
        res = super()._get_model_to_field_name()
        res.update(
            {
                "sale.order.line": "sale_line_id",
            }
        )
        return res
