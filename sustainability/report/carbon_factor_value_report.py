from odoo import api, fields, models


class CarbonFactorValueReport(models.Model):
    _name = "carbon.factor.value.report"
    _description = "Emission Factors By Vintage"
    _auto = False
    _rec_name = "date"
    _order = "date desc"

    # ==== Carbon Factor Value fields ====
    date = fields.Date(readonly=True)
    type_id = fields.Many2one("carbon.factor.type", string="Type", readonly=True)
    factor_id = fields.Many2one("carbon.factor", string="Factor", readonly=True)
    carbon_uom_id = fields.Many2one("uom.uom", string="Unit of measure", readonly=True)
    carbon_value = fields.Float(
        string="Average CO2 (kg)", readonly=True, group_operator="avg"
    )

    # ==== Carbon Factor fields ====
    name = fields.Char(readonly=True)
    carbon_database_id = fields.Many2one(
        "carbon.factor.database", string="Database", readonly=True
    )
    carbon_contributor_id = fields.Many2one(
        "carbon.factor.contributor", string="Contributor", readonly=True
    )
    carbon_compute_method = fields.Selection(
        selection=[("physical", "Physical"), ("monetary", "Monetary")],
        string="Compute Method",
        readonly=True,
    )
    ghg_view_mode = fields.Boolean(string="Show greenhouse gases detail", readonly=True)
    active = fields.Boolean(readonly=True)
    uncertainty_percentage = fields.Float(string="Uncertainty (%)", readonly=True)
    country_id = fields.Many2one("res.country", string="Country", readonly=True)
    country_group_id = fields.Many2one(
        "res.country.group", string="Country Group", readonly=True
    )
    category = fields.Char(readonly=True)
    root = fields.Char(readonly=True)
    parent_id = fields.Many2one(
        comodel_name="carbon.factor", string="Parent", readonly=True
    )

    @property
    def _table_query(self):
        return f"{self._select()} {self._from()} {self._where()}"

    @api.model
    def _select(self):
        return """
            SELECT
                cfv.id AS id,
                cfv.date AS date,
                cfv.type_id AS type_id,
                cfv.factor_id AS factor_id,
                cfv.carbon_uom_id AS carbon_uom_id,
                cfv.carbon_value AS carbon_value,
                cf.name AS name,
                cf.carbon_database_id AS carbon_database_id,
                cf.carbon_contributor_id AS carbon_contributor_id,
                cf.carbon_compute_method AS carbon_compute_method,
                cf.active AS active,
                cf.ghg_view_mode AS ghg_view_mode,
                cf.uncertainty_percentage AS uncertainty_percentage,
                cf.country_id AS country_id,
                cf.country_group_id AS country_group_id,
                cf.category AS category,
                cf.root AS root,
                cf.parent_id AS parent_id
        """

    @api.model
    def _from(self):
        return """
            FROM carbon_factor_value cfv
            INNER JOIN carbon_factor cf ON cf.id = cfv.factor_id
        """

    @api.model
    def _where(self):
        return """
            WHERE cfv.date IS NOT NULL
        """
