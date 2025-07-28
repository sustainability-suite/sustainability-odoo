from odoo import api, fields, models


class SustainabilityStockFreightComputation(models.Model):
    _name = "sustainability.stock.freight.computation"
    _description = "Freight Computation"

    origin = fields.Char()
    destination = fields.Char()
    co2_ratio = fields.Float()
    weight_unit = fields.Char(string="Unit")
    transport_mode = fields.Char()
    co2_display = fields.Char(
        string="CO2 ratio", compute="_compute_co2_display", store=False
    )
    api_response = fields.Text()
    request_payload = fields.Text()
    error_message = fields.Text()

    @api.depends("co2_ratio", "weight_unit")
    def _compute_co2_display(self):
        for record in self:
            record.co2_display = f"{record.co2_ratio:.6f} kgCO2e/{record.weight_unit}"
