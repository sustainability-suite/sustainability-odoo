from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Add carbon factor fields to product loading parameters."""
        fields = super()._load_pos_data_fields(config_id)
        fields.append("carbon_out_factor_id")
        return fields


class CarbonFactor(models.Model):
    _inherit = "carbon.factor"

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Define loading fields for carbon.factor model."""
        return ["id", "name", "carbon_value"]

    @api.model
    def _load_pos_data_domain(self, data):
        """Define domain for loading carbon.factor records."""
        return []

    def _load_pos_data(self, data):
        """Load carbon factor data for POS."""
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(data["pos.config"])

        return {
            "data": self.search_read(domain, fields),
            "fields": fields,
        }


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.model
    def _load_pos_data_models(self, config_id):
        """Add carbon.factor to the list of models to load."""
        result = super()._load_pos_data_models(config_id)
        result.append("carbon.factor")
        return result
