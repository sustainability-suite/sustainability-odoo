import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class CarbonLineOrigin(models.Model):
    _name = "carbon.line.origin"
    _description = "carbon.line.origin"

    # Fake Many2one that is used in the One2many field in `carbon.line.mixin`
    res_model_id = fields.Many2one(
        "ir.model", index=True, ondelete="cascade", required=True
    )
    res_model = fields.Char(
        related="res_model_id.model",
        index=True,
        precompute=True,
        store=True,
        readonly=True,
        string="Model",
    )
    res_id = fields.Many2oneReference(
        index=True, model_field="res_model", string="Res id"
    )
    factor_value_id = fields.Many2one("carbon.factor.value", string="Factor value")

    value = fields.Float(
        digits="Carbon value", required=True, string="Factor Value"
    )  # Result of the computation (might be a partial result)
    signed_value = fields.Float(
        compute="_compute_signed_value",
        store=True,
        digits="Carbon value",
        string="Total",
    )
    distribution = fields.Float()
    carbon_value = fields.Float(digits="Carbon Factor value", string="Value")
    uncertainty_percentage = fields.Float(default=0.0, string="Uncertainty")
    uncertainty_value = fields.Float(default=0.0, digits="Carbon Factor value")
    signed_uncertainty_value = fields.Float(
        compute="_compute_signed_uncertainty_value",
        store=True,
        digits="Carbon value",
    )
    compute_method = fields.Char()
    uom_id = fields.Many2one("uom.uom")
    monetary_currency_id = fields.Many2one("res.currency", string="Currency")
    carbon_data_uncertainty_percentage = fields.Float(
        related="move_line_id.carbon_data_uncertainty_percentage",
        store=False,
        readonly=True,
    )
    comment = fields.Char()

    factor_id = fields.Many2one(
        related="factor_value_id.factor_id", string="Emission Factor", store=True
    )
    factor_value_type_id = fields.Many2one(
        related="factor_value_id.type_id", string="Factor Value Type", store=True
    )

    factor_category_id = fields.Many2one(
        related="factor_id.parent_id", string="Factor Category", store=True
    )
    factor_database_id = fields.Many2one(
        related="factor_id.carbon_database_id",
        string="Database",
        store=True,
    )
    factor_contributor_id = fields.Many2one(
        related="factor_id.carbon_contributor_id",
        string="Contributor",
        store=True,
    )
    computation_level = fields.Char()

    # --------------------------------------------
    #          account.move.line fields
    # --------------------------------------------
    move_line_id = fields.Many2one(
        "account.move.line",
        compute="_compute_many2one_lines",
        store=True,
        string="Journal Item",
    )
    move_id = fields.Many2one(
        related="move_line_id.move_id", store=True, string="Journal Entry"
    )
    move_company_currency_id = fields.Many2one(
        string="Company Currency",
        related="move_id.company_currency_id",
        readonly=True,
        store=False,
    )
    move_date = fields.Date(
        related="move_id.date", string="Invoice Date", readonly=True, store=True
    )
    move_state = fields.Selection(
        related="move_id.state", string="Status", readonly=True
    )
    move_line_account_id = fields.Many2one(
        related="move_line_id.account_id", store=True, string="Account"
    )
    move_line_partner_id = fields.Many2one(
        related="move_line_id.partner_id", store=True, string="Partner"
    )
    move_line_journal_id = fields.Many2one(
        related="move_line_id.journal_id", store=True, string="Journal"
    )
    move_line_balance = fields.Monetary(
        related="move_line_id.balance",
        string="Balance",
        readonly=True,
        store=False,
        currency_field="move_company_currency_id",
    )
    move_line_label = fields.Char(
        related="move_line_id.name",
        string="Label",
        store=False,
        readonly=True,
    )
    move_line_quantity = fields.Float(
        related="move_line_id.quantity",
        string="Quantity",
        store=False,
        readonly=True,
    )
    move_line_product_uom_id = fields.Many2one(
        related="move_line_id.product_uom_id",
        string="Unit of Measure",
        store=False,
        readonly=True,
    )

    @api.model
    def _get_model_to_field_name(self) -> dict[str, str]:
        return {
            "account.move.line": "move_line_id",
        }

    """
    Real many2one fields that are computed from the fake Many2one
    Other fields are in submodules:
    - sustainability_purchase: purchase_line_id
    - sustainability_hr_expense_report: expense_id
    - etc...

    These are useful to create related fields!
    """

    @api.depends("res_model", "res_id")
    def _compute_many2one_lines(self):
        """Update the corresponding many2one field on the line"""
        model_to_field_name = self._get_model_to_field_name()
        default_vals = {
            field_name: False for field_name in model_to_field_name.values()
        }

        for origin in self:
            vals = {**default_vals}
            if origin.res_model in model_to_field_name:
                vals[model_to_field_name[origin.res_model]] = origin.res_id
            origin.update(vals)

    @api.depends("value", "res_id", "res_model")
    def _compute_signed_value(self):
        for origin in self:
            origin.signed_value = origin.value * origin.get_record().get_carbon_sign()

    @api.depends("uncertainty_value", "res_id", "res_model")
    def _compute_signed_uncertainty_value(self):
        for origin in self:
            origin.signed_uncertainty_value = (
                origin.uncertainty_value * origin.get_record().get_carbon_sign()
            )

    def get_record(self):
        """Return the record that generated this origin"""
        self.ensure_one()
        if self.res_model in self.env:
            if fname := self._get_model_to_field_name().get(self.res_model):
                return self[fname]
            _logger.warning(
                "CarbonLineOrigin: Many2one field for model `%s` does not exist, which is probably not intended",
                self.res_model,
            )
            return self.env[self.res_model].browse(self.res_id).exists()
        raise ValueError(f"Model {self.res_model} not found")

    @api.model
    def _clean_orphan_lines(self):
        """
        Extra-cleaning method to remove lines that have no origin
        Mid-term goal is to deprecate it/remove it. The logger is here to help us doing this decision.
        """
        lines_to_remove = self.search([("res_id", "in", [0, False])])
        if lines_to_remove:
            _logger.warning(
                "CarbonLineOrigin: %s lines will be removed because they have no origin",
                len(lines_to_remove),
            )
            lines_to_remove.unlink()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self._clean_orphan_lines()
        return res

    # --------------------------------------------
    #                   ACTIONS
    # --------------------------------------------

    def action_open_record(self):
        self.ensure_one()
        if record := self.get_record():
            action = record.get_formview_action()
            action["target"] = "new"
            return action
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Error"),
                "message": _(
                    "Couldn't open record: %s,%s", self.res_model, self.res_id
                ),
                "type": "danger",
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
