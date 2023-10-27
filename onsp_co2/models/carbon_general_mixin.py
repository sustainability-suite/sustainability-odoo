from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError


class CarbonGeneralMixin(models.AbstractModel):
    _name = "carbon.general.mixin"
    _description = "A general mixin used to compute carbon values"


    def _get_record_description(self) -> str:
        self.ensure_one()
        return self._description + (f": {self.name}" if hasattr(self, 'name') else "")



    def get_related_carbon_factor(self, prefix: str):
        """
        If the record is linked to a carbon factor, return this latter. There are 2 scenarios:
            - Either carbon mode is manual and factor_id is set
            - Or carbon mode is auto and the fallback record is a carbon factor
        """
        if getattr(self, f"{prefix}_mode") == 'manual':
            return getattr(self, f"{prefix}_factor_id")
        elif getattr(self, f"{prefix}_mode") == 'auto':
            fallback_record = getattr(self, f"{prefix}_fallback_reference")
            if fallback_record and fallback_record._name == 'carbon.factor':
                return fallback_record
        return None

    def get_carbon_value(self, carbon_type: str = None, quantity: float = None, from_uom_id=None, amount: float = None, from_currency_id=None, date=None, data_uncertainty_value: float = 0.0) -> tuple[float, dict]:
        """
        Return a value computed depending on the calculation method of carbon (qty/price) and the type of operation (credit/debit)
        Used in account.move.line to compute carbon debt if a product is set.
        """
        self.ensure_one()

        if self._name == 'carbon.factor':
            factor = self
        else:
            # Todo someday: make carbon type list extensible
            # Carbon type is not mandatory for carbon factors, but it is for other records (that inherit `carbon.mixin`)
            if carbon_type not in ['in', 'out']:
                raise UserError(_("Carbon value type must be either 'in' or 'out'"))
            prefix = 'carbon_' + carbon_type
            factor = self.get_related_carbon_factor(prefix)


        if factor:
            """ Either:
                1) carbon mode is manual and factor_id is set
                2) carbon mode is auto and the fallback record is a carbon factor
                3) self is a carbon factor
            """
            infos = factor.get_value_infos_at_date(date)
        else:
            """ Either:
                1) carbon mode is manual and factor_id is False
                2) carbon mode is auto and the fallback record is not a carbon factor
            """
            infos = {
                'compute_method': getattr(self, f"{prefix}_compute_method"),
                'carbon_value': getattr(self, f"{prefix}_value"),
                'carbon_value_origin': getattr(self, f"{prefix}_value_origin"),
                'carbon_uom_id': getattr(self, f"{prefix}_uom_id"),
                'carbon_monetary_currency_id': getattr(self, f"{prefix}_monetary_currency_id"),
            }


        if infos['compute_method'] == "physical" and quantity is not None and from_uom_id:
            if from_uom_id.category_id != infos['carbon_uom_id'].category_id:
                raise ValidationError(_(
                    "The unit of measure set for %s (%s - %s) is not in the same category as its carbon unit of measure (%s - %s)\nPlease check the carbon settings.",
                    self.display_name,
                    from_uom_id.name,
                    from_uom_id.category_id.name,
                    infos['carbon_uom_id'].name,
                    infos['carbon_uom_id'].category_id.name,
                ))

            value = infos['carbon_value'] * from_uom_id._compute_quantity(quantity, infos['carbon_uom_id'])

        elif infos['compute_method'] == "monetary" and amount is not None and from_currency_id:
            # We convert the amount to the currency used in carbon settings of the record
            date = date or fields.Date.today()
            value = infos['carbon_value'] * from_currency_id._convert(amount, infos['carbon_monetary_currency_id'], self.env.company, date)

        else:
            raise ValidationError(_("To compute a carbon cost, you must pass:"
                              "\n- either a quantity and a unit of measure"
                              "\n- or a price and a currency (+ an optional date)"
                              "\n\nPassed value: "
                              "\n- Record: %s (compute method: %s)"
                              "\n- Quantity: %s, UOM: %s"
                              "\n- Amount: %s, Currency: %s", self, infos['compute_method'], quantity, from_uom_id, amount, from_currency_id))


        if factor:
            infos['uncertainty_value'] = ((factor.uncertainty_value**2 + data_uncertainty_value**2) ** 0.5) * value

        return value, infos


