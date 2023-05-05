from odoo import api, fields, models


class CarbonFactor(models.Model):
    _name = "carbon.factor"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Carbon Emission Factor"
    _order = "display_name"
    _parent_store = True

    _sql_constraints = [
        ('not_negative_carbon_value', 'CHECK(carbon_value >= 0)', 'CO2e value can not be negative !'),
    ]

    name = fields.Char(required=True)
    display_name = fields.Char(compute="_compute_display_name", store=True, recursive=True)
    parent_id = fields.Many2one('carbon.factor', "Parent", index=True, ondelete='restrict')
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many("carbon.factor", "parent_id")

    carbon_value = fields.Float(
        string="CO2e value",
        digits="Carbon value",
        # currency_field='carbon_currency_id',
        tracking=True,
    )
    carbon_currency_id = fields.Many2one(
        'res.currency',
        compute="_compute_carbon_currency_id",
    )
    carbon_currency_label = fields.Char(compute="_compute_carbon_currency_id")

    # Depending on factor type, there is either a carbon_uom_id or a carbon_monetary_currency_id
    carbon_compute_method = fields.Selection(
        selection=[
            ('physical', 'Physical'),
            ('monetary', 'Monetary'),
        ],
        default=False,
    )
    carbon_uom_id = fields.Many2one("uom.uom")
    carbon_monetary_currency_id = fields.Many2one("res.currency")
    unit_label = fields.Char(compute="_compute_unit_label", string=" ")

    # Todo in 2nd "sprint": implement uuid, values model, etc......
    # uuid = fields.Char()


    def name_get(self) -> list[tuple[int, str]]:
        return [(factor.id, factor.display_name) for factor in self]

    # Useful in carbon.mixin, but this model does not inherit it, so I add it manually.
    # Might be useful to create a more general mixin if this happens again
    def _get_record_description(self) -> str:
        self.ensure_one()
        return f"{self._description}: {self.name}"


    def _compute_carbon_currency_id(self):
        for factor in self:
            factor.carbon_currency_id = self.env.ref("onsp_co2.carbon_kilo", raise_if_not_found=False)
            factor.carbon_currency_label = factor.carbon_currency_id.currency_unit_label

    @api.depends('parent_id.display_name', 'name')
    def _compute_display_name(self):
        for factor in self:
            factor.display_name = f"{factor.parent_id.display_name}/{factor.name}" if factor.parent_id else factor.name

    @api.depends('carbon_compute_method', 'carbon_monetary_currency_id', 'carbon_uom_id')
    def _compute_unit_label(self):
        for factor in self:
            if not factor.carbon_compute_method or not (factor.carbon_uom_id or factor.carbon_monetary_currency_id):
                factor.unit_label = ""
            else:
                factor.unit_label = "/ " + (factor.carbon_uom_id.name or factor.carbon_monetary_currency_id.currency_unit_label)



