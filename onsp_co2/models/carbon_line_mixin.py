from odoo import api, fields, models, _
from typing import Union, Any
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)



class CarbonLineMixin(models.AbstractModel):
    _name = "carbon.line.mixin"
    _description = "carbon.line.mixin"

    carbon_currency_id = fields.Many2one(
        'res.currency',
        compute="_compute_carbon_currency_id",
    )
    carbon_debt = fields.Monetary(
        string="CO2 Debt",
        currency_field="carbon_currency_id",
        help="A positive value means that your system's debt grows, a negative value means it shrinks",
        compute="_compute_carbon_debt",
        readonly=False,
        store=True,
    )
    carbon_uncertainty_value = fields.Monetary(
        compute="_compute_carbon_debt",
        currency_field="carbon_currency_id",
        string="CO2 Uncertainty",
        readonly=False,
        store=True,
    )
    carbon_is_locked = fields.Boolean(default=False)

    # Both fields are Char because they are only informative and we won't do any computation on them
    carbon_origin_name = fields.Char(compute="_compute_carbon_debt", string="CO2e origin", store=True)
    carbon_origin_value = fields.Char(compute="_compute_carbon_debt", string="CO2e origin value", store=True)



    # --------------------------------------------
    #             Methods to override
    # --------------------------------------------


    @api.model
    def _get_states_to_auto_recompute(self) -> list[str]:
        """ Return a list of states used to filter which lines need to be recomputed (used in `_get_lines_to_compute_domain`) """
        raise NotImplementedError()

    @api.model
    def _get_state_field_name(self) -> str:
        """ Each line model has its own state field name, return it here """
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
            'amount': self._get_line_amount(),
            # You should override it with a more precise value (e.g. currency of the invoice for account.move.line)
            'from_currency_id': self.env.company.currency_id,
        }

    def _get_line_amount(self) -> float:
        """ Return the value used to compute carbon for the line ONLY in case of monetary computation """
        raise NotImplementedError()

    def _get_carbon_compute_default_record(self) -> Any:
        """ Return the record used to compute carbon for the line (often a company) """
        self.ensure_one()
        return self.env.company   # This should be the absolute last resort, you should override it




    # --------------------------------------------


    @api.onchange('carbon_debt')
    def _onchange_carbon_debt(self):
        self.update({
            'carbon_origin_name': _("Manual"),
            'carbon_origin_value': '-',
        })

    def _compute_carbon_currency_id(self):
        for move in self:
            move.carbon_currency_id = self.env.ref("onsp_co2.carbon_kilo", raise_if_not_found=False)

    """
        The 2 following methods are used to filter lines that need to be recomputed.
        They are split to provide 2 hooks for a better modularity.
    """

    def _get_lines_to_compute_domain(self, force_compute: list[str]):
        """ Build a domain to filter lines that need to be recomputed """
        domain = []
        if 'all_states' not in force_compute:
            domain.append((self._get_state_field_name(), 'in', self._get_states_to_auto_recompute()))
        if 'locked' not in force_compute:
            domain.append(('carbon_is_locked', '=', False))
        return domain

    def _filter_lines_to_compute(self, force_compute: Union[bool, str, list[str]] = None):
        """ Used in _compute_carbon_debt to filter lines that need to be recomputed """
        if force_compute is None:
            force_compute = []
        elif isinstance(force_compute, bool):
            force_compute = ['all_states', 'locked'] if force_compute else []
        elif isinstance(force_compute, str):
            force_compute = [force_compute]

        domain = self._get_lines_to_compute_domain(force_compute=force_compute)
        return self.filtered_domain(domain)




    """ depends need to be overriden to trigger the compute method at the right time """
    @api.depends()
    def _compute_carbon_debt(self, force_compute: Union[bool, str, list[str]] = None):
        lines_to_compute = self._filter_lines_to_compute(force_compute=force_compute)

        for line in lines_to_compute:
            kw_arguments = line._get_carbon_compute_kwargs()

            for field in line._get_carbon_compute_possible_fields():
                if getattr(line, f"can_use_{field}_carbon_value", lambda: False)():
                    record = getattr(line, field)
                    # Extra check to make sure the record has the method that we need
                    if hasattr(record, 'get_carbon_value'):
                        kw_arguments.update(getattr(line, f"get_{field}_carbon_compute_values", lambda: {})())
                        break
            else:
                record = line._get_carbon_compute_default_record()

            debt, infos = record.get_carbon_value(**kw_arguments)
            line.carbon_debt = debt
            line.carbon_uncertainty_value = infos.get('uncertainty_value', 0.0)
            line.carbon_origin_name = infos['carbon_value_origin']
            line.carbon_origin_value = infos['carbon_value']




    # --------------------------------------------
    #                ACTION / UI
    # --------------------------------------------
    # Todo: replace these methods with an OWL widget?


    def action_see_carbon_origin(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': f"CO2e Value: {self.carbon_origin_value}",
                'message': self.carbon_origin_name,
                'type': 'info',
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def action_recompute_carbon(self) -> dict:
        """ Force re-computation of carbon values for lines. Todo: add a confirm dialog if a subset is 'posted' """
        for line in self:
            line._compute_carbon_debt(force_compute='all_states')
        return {}

    def action_switch_locked(self):
        for line in self:
            line.carbon_is_locked = not line.carbon_is_locked

