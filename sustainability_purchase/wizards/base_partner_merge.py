import itertools
import logging
from collections import defaultdict

from odoo import api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger("odoo.addons.base.partner.merge")


class BasePartnerMergeAutomaticWizard(models.TransientModel):
    _inherit = "base.partner.merge.automatic.wizard"

    @api.model
    def _update_values(self, src_partners, dst_partner):
        """Copied from
        https://github.com/odoo/odoo/blob/9d4f8b2fda5c75438ad30a08b4f7d95eac4f2f23/odoo/addons/base/wizard/base_partner_merge.py#L240

        The native function can't merge fields of type `reference` because it is never user by Odoo on model `res.partner`.
        In this addon, we use a `reference` field on `res.parnter`, so this wizard needs to support them.
        """
        _logger.debug(
            "_update_values for dst_partner: %s for src_partners: %r",
            dst_partner.id,
            src_partners.ids,
        )

        model_fields = dst_partner.fields_get().keys()
        summable_fields = self._get_summable_fields()

        def write_serializer(item):
            if isinstance(item, models.BaseModel):
                return item.id
            else:
                return item

        # get all fields that are not computed or x2many
        values = dict()
        values_by_company = defaultdict(dict)  # {company: vals}
        for column in model_fields:
            field = dst_partner._fields[column]
            if field.type not in ("many2many", "one2many") and field.compute is None:
                for item in itertools.chain(src_partners, [dst_partner]):
                    if item[column]:
                        if field.type == "reference":
                            values[column] = f"{item[column]._name},{item[column].id}"
                        elif column in summable_fields and values.get(column):
                            values[column] += write_serializer(item[column])
                        else:
                            values[column] = write_serializer(item[column])
            elif field.company_dependent and column in summable_fields:
                # sum the values of partners for each company; use sudo() to
                # compute the sum on all companies, including forbidden ones
                partners = (src_partners + dst_partner).sudo()
                for company in self.env["res.company"].sudo().search([]):
                    values_by_company[company][column] = sum(
                        partners.with_company(company).mapped(column)
                    )

        # remove fields that can not be updated (id and parent_id)
        values.pop("id", None)
        parent_id = values.pop("parent_id", None)
        dst_partner.write(values)
        for company, vals in values_by_company.items():
            dst_partner.with_company(company).sudo().write(vals)
        # try to update the parent_id
        if parent_id and parent_id != dst_partner.id:
            try:
                dst_partner.write({"parent_id": parent_id})
            except ValidationError:
                _logger.info(
                    "Skip recursive partner hierarchies for parent_id %s of partner: %s",
                    parent_id,
                    dst_partner.id,
                )
