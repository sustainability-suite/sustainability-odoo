import {registry} from "@web/core/registry";
import {stepUtils} from "@web_tour/tour_service/tour_utils";

registry.category("web_tour.tours").add("create_journal_entry", {
    url: "/odoo/accounting?debug=1",
    steps: () => [
        {
            trigger: ".o-dropdown[data-menu-xmlid='account\\.menu_finance_entries']",
            run: "click",
            content: "Click on Accounting",
        },
        {
            trigger:
                ".o-dropdown-item[data-menu-xmlid='account\\.menu_action_move_journal_line_form']",
            run: "click",
            content: "Click on Journal Entries",
        },
        {
            trigger: ".o_list_button_add",
            run: "click",
            content: "Create new invoice",
        },
        {
            trigger: ".o_field_x2many_list_row_add > a",
            run: "click",
            content: "Add a line",
        },
        {
            trigger: ".o_field_widget[name='account_id'] .o-autocomplete--input",
            content: "Open account dropdown",
            run: "click",
        },
        {
            trigger: ".o-autocomplete--dropdown-item:nth-child(1) > a",
            content: "Select account",
            run: "click",
        },
        ...stepUtils.saveForm(),
    ],
});
