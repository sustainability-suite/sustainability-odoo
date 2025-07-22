# © 2025 Open Net Sarl
# License LGPL-3 or later (https://www.gnu.org/licenses/agpl).

import copy

from odoo import api, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        """
        The module l10n_ch_hr_payroll_elm_transmission erases the classic notebook inside the employee form.
        This override is used to add a new page to the employee form.
        """
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
            for commuting_node in arch.xpath("//page[@name='commuting_settings']"):
                new_node = copy.deepcopy(commuting_node)
                new_node.set("name", "commuting_settings_l10n_ch")
                arch.xpath("//notebook")[0].append(new_node)
        return arch, view
