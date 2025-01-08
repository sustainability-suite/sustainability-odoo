import logging
from typing import Any

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class CarbonLineMixin(models.AbstractModel):
    _name = "carbon.line.mixin"
    _description = "carbon.line.mixin"

    carbon_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_carbon_currency_id",
    )
    carbon_debt = fields.Monetary(
        string="CO2",
        currency_field="carbon_currency_id",
        help="A positive value means that your system's debt grows, a negative value means it shrinks",
        compute="_compute_carbon_debt",
        readonly=False,
        store=True,
    )
    carbon_data_uncertainty_percentage = fields.Float(
        string="CO2 Uncertainty %",
        default=lambda self: self.env.company.carbon_default_data_uncertainty_percentage,
    )
    carbon_uncertainty_value = fields.Monetary(
        compute="_compute_carbon_debt",
        currency_field="carbon_currency_id",
        string="CO2 Uncertainty",
        readonly=False,
        store=True,
    )
    carbon_is_locked = fields.Boolean(default=False)

    carbon_origin_json = fields.Json(
        compute="_compute_carbon_debt",
        store=True,
    )
    carbon_origin_ids = fields.One2many(
        "carbon.line.origin",
        "res_id",
        "Carbon value origin details",
        auto_join=True,
    )

    # --------------------------------------------
    #             Methods to override
    # --------------------------------------------

    @api.model
    def _get_states_to_auto_recompute(self) -> list[str]:
        """Return a list of states used to filter which lines need to be recomputed (used in `_get_lines_to_compute_domain`)"""
        raise NotImplementedError()

    @api.model
    def _get_state_field_name(self) -> str:
        """Each line model has its own state field name, return it here"""
        raise NotImplementedError()

    @api.model
    def _get_carbon_compute_possible_fields(self) -> list[str]:
        """
        Elements order matters as the first valid field will be used.
        After adding a field name, you should add 2 methods named:
        - `can_use_{field_name}_carbon_value`: return a bool
        - `get_{field_name}_carbon_compute_values`: return a dict with extra values to pass to the `get_carbon_value` method

        check account_move_line.py to see an example
        """
        raise NotImplementedError()

    def _get_carbon_compute_kwargs(self) -> dict:
        """
        Override this method to pass extra kwargs to `get_carbon_value`
        `carbon_type` key is mandatory so you'll need to override it (with a different logic depending on the model)

        Other common keys are:
            - from_currency_id
            - date

        Specific keys will be passed in methods named `get_{field_name}_carbon_compute_values`
            > see `_get_carbon_compute_possible_fields` doc
        """
        self.ensure_one()
        return {
            # Amount is mandatory because the fallback value is monetary computed (on company level)
            "amount": self._get_line_amount(),
            # You should override the currency with a more precise value (e.g. currency of the invoice for account.move.line)
            "from_currency_id": self.env.company.currency_id,
            "data_uncertainty_percentage": self.carbon_data_uncertainty_percentage,
        }

    def _get_line_amount(self) -> float:
        """Return the value used to compute carbon for the line ONLY in case of monetary computation"""
        raise NotImplementedError()

    def _get_carbon_compute_default_record(self) -> Any:
        """Return the record used to compute carbon for the line (often a company)"""
        self.ensure_one()
        return (
            self.env.company
        )  # This should be the absolute last resort, you should override it

    def get_carbon_sign(self) -> int:
        """
        Return the sign of the carbon value (1 or -1)
        Mainly used for account.move.line to determine if the line is a credit or a debit
        """
        return 1

    def _get_computation_levels_mapping(self) -> dict:
        return {
            "account.move.line": _("Carbon on invoice"),
            "product.product": _("Product"),
            "product.category": _("Product category"),
            "product.template": _("Product template"),
            "res.partner": _("Partner"),
            "account.account": _("Account"),
            "res.company": _("Company fallback"),
        }

    # --------------------------------------------

    @api.onchange("carbon_debt")
    def _onchange_carbon_debt(self):
        self.update(
            {
                "carbon_uncertainty_value": 0.0,
                "carbon_data_uncertainty_percentage": 0.0,
                "carbon_origin_json": {
                    "mode": "manual",
                    "details": {"uid": self.env.uid, "username": self.env.user.name},
                    "model_name": self._name,
                },
            }
        )

    def _compute_carbon_currency_id(self):
        for move in self:
            move.carbon_currency_id = self.env.ref(
                "sustainability.carbon_kilo", raise_if_not_found=False
            )

    """
        The 2 following methods are used to filter lines that need to be recomputed.
        They are split to provide 2 hooks for a better modularity.
    """

    def _get_lines_to_compute_domain(self, force_compute: list[str]):
        """Build a domain to filter lines that need to be recomputed"""
        # Todo: check if tmp or fine
        domain = [("carbon_origin_json", "=", False)]
        if "all_states" not in force_compute:
            domain.append(
                (
                    self._get_state_field_name(),
                    "in",
                    self._get_states_to_auto_recompute(),
                )
            )
        if "locked" not in force_compute:
            domain.append(("carbon_is_locked", "=", False))
        return domain

    def _filter_lines_to_compute(self, force_compute=None):
        """Used in _compute_carbon_debt to filter lines that need to be recomputed"""
        if force_compute is None:
            force_compute = []
        elif isinstance(force_compute, bool):
            force_compute = ["all_states", "locked"] if force_compute else []
        elif isinstance(force_compute, str):
            force_compute = [force_compute]

        domain = self._get_lines_to_compute_domain(force_compute=force_compute)
        return self.filtered_domain(domain)

    """ depends need to be overriden to trigger the compute method at the right time """

    @api.depends("carbon_data_uncertainty_percentage")
    def _compute_carbon_debt(self, force_compute=None):
        """
        Choose the right factor(s) to compute carbon value, store it with the details of the computation
        """
        lines_to_compute = self._filter_lines_to_compute(force_compute=force_compute)
        skipped_lines = self.env[self._name]

        for line in lines_to_compute:
            kw_arguments = line._get_carbon_compute_kwargs()

            for field in line._get_carbon_compute_possible_fields():
                if getattr(line, f"can_use_{field}_carbon_value", lambda: False)():
                    kw_arguments.update(
                        getattr(
                            line, f"get_{field}_carbon_compute_values", lambda: {}
                        )()
                    )
                    record = line[field]
                    break
            else:
                record = line._get_carbon_compute_default_record()

            # Check if we can use the chosen record or its fallback instead
            carbon_type = kw_arguments["carbon_type"]
            if not record.has_valid_carbon_value(carbon_type):
                if record.has_valid_carbon_fallback(carbon_type):
                    record = record[f"carbon_{carbon_type}_fallback_reference"]
                else:
                    # This shouldn't happen if can_use_X_carbon_value is well implemented
                    _logger.warning(
                        f"Skip carbon compute for {line._name}({line.id}) - '{line.display_name}' (last incorrect fallback: {record._name}({record.id}) '{record.display_name}') -  this line"
                    )
                    skipped_lines |= line
                    continue

            factors, distribution, model_name = record.get_carbon_distribution(
                carbon_type
            )
            debt, uncertainty_value, details = factors.get_carbon_value(
                distribution, **kw_arguments
            )

            line.carbon_debt = debt
            line.carbon_uncertainty_value = uncertainty_value
            line.carbon_origin_json = {
                "mode": "auto",
                "details": details,
                "model_name": model_name,
            }

        return skipped_lines

    def _get_line_origin_vals_list(self) -> list[dict]:
        """Return the vals used to create a carbon.line.origin record"""
        self.ensure_one()
        today = fields.Date.today()
        res_model_id = self.env["ir.model"]._get_id(self._name)
        res_id = self.id or self.id.origin
        vals_list = list()

        mode = self.carbon_origin_json.get("mode")
        json_details = self.carbon_origin_json.get("details", {})
        model_name = self.carbon_origin_json.get("model_name", "")

        if mode == "manual":
            vals_list.append(
                {
                    "res_model_id": res_model_id,
                    "res_id": res_id,
                    # Todo: don't set the string here but in the onchange
                    "comment": _(
                        "Manually set on %s by %s",
                        today,
                        json_details.get("username", _("Unknown User")),
                    ),
                    "value": self.carbon_debt,
                    "carbon_data_uncertainty_percentage": self.carbon_data_uncertainty_percentage,
                    "uncertainty_value": self.carbon_uncertainty_value,
                    "computation_level": self._get_computation_levels_mapping().get(
                        model_name
                    ),
                }
            )

        elif mode == "auto":
            for _factor, value_to_details in json_details.items():
                for factor_value, details in value_to_details.items():
                    vals_list.append(
                        {
                            "res_model_id": res_model_id,
                            "res_id": res_id,
                            # Needed because json keys are strings
                            "factor_value_id": int(factor_value),
                            "comment": _("Computation made on %s", today),
                            **details,
                            "uom_id": details.get("uom_id"),
                            "monetary_currency_id": details.get("monetary_currency_id"),
                            "computation_level": self._get_computation_levels_mapping().get(
                                model_name
                            ),
                        }
                    )

        return vals_list

    @api.model
    def _create_origin_lines(self):
        origin_vals_list = list()
        lines_to_flush = self.search([("carbon_origin_json", "!=", False)])

        for line in lines_to_flush:
            line.carbon_origin_ids.unlink()
            origin_vals_list.extend(line._get_line_origin_vals_list())

        # To avoid empty create calls
        if origin_vals_list:
            self.env["carbon.line.origin"].create(origin_vals_list)

        lines_to_flush.carbon_origin_json = False

    def write(self, vals):
        res = super().write(vals)
        self._create_origin_lines()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._create_origin_lines()
        return res

    def unlink(self):
        self.carbon_origin_ids.unlink()
        return super().unlink()

    # --------------------------------------------
    #                ACTION / UI
    # --------------------------------------------
    # Todo: replace these methods with an OWL widget?

    def action_see_carbon_origin(self):
        self.ensure_one()
        return {
            "name": _("CO2 origin details for %s", self.display_name),
            "type": "ir.actions.act_window",
            "res_model": "carbon.line.origin",
            "views": [[False, "tree"]],
            "domain": [("id", "in", self.carbon_origin_ids.ids)],
            "target": "current",
            "context": {
                **self.env.context,
            },
        }

    def action_recompute_carbon(self) -> dict:
        """Force re-computation of carbon values for lines"""
        skipped_lines = self._compute_carbon_debt(force_compute="all_states")
        if skipped_lines:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("%s lines couldn't be recomputed", len(skipped_lines)),
                    "message": _("Check server logs for more details"),
                    "type": "warning",
                    "sticky": False,
                },
            }
        return {}

    def action_switch_locked(self):
        for line in self:
            line.carbon_is_locked = not line.carbon_is_locked
