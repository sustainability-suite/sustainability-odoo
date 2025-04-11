import {registry} from "@web/core/registry";
import {stepUtils} from "@web_tour/tour_service/tour_utils";

import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {stepUtils} from "@web_tour/tour_service/tour_utils";

registry.category("web_tour.tours").add("create_journal_entry", {
    url: "/web",
    steps: () => [
        ...stepUtils.goToAppSteps("account.menu_finance"),
        {
            trigger: '.dropdown button[data-menu-xmlid="account.menu_finance_entries"]',
            content: "Click on Accounting",
            position: "bottom",
        },
        {
            trigger: 'a[data-menu-xmlid="account.menu_action_move_journal_line_form"]',
            content: "Click on Journal Entries",
            position: "bottom",
        },
        {
            trigger: "button.o_list_button_add",
            content: "Create new invoice",
            position: "bottom",
        },
        {
            trigger: ".o_field_x2many_list_row_add > a",
            content: "Add a line",
            position: "bottom",
            run: "click",
        },
        {
            trigger: ".o_field_widget[name='account_id'] .o-autocomplete--input",
            content: "Open account dropdown",
            position: "bottom",
            run: "click",
        },
        {
            trigger: ".o-autocomplete--dropdown-item:nth-child(1) > a",
            content: "Select account",
            position: "bottom",
            run: "click",
        },
        ...stepUtils.saveForm(),
    ],
});
