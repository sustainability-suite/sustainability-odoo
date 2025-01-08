/** @odoo-module **/

import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {_lt} from "@web/core/l10n/translation";

import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";
import {CarbonSettings} from "@sustainability/owl/carbon_settings/carbon_settings";

export class CarbonSettingsPanel extends Component {
    setup() {
        super.setup();
        this.carbon_types = this.props.types.split(",");
    }
    getCarbonTitle(type) {
        let options = this.props.options[type];
        return options && "title" in options ? options.title : "";
    }
    getShowDistribution(type) {
        let options = this.props.options[type];
        return options && "show_distribution" in options
            ? options.show_distribution
            : false;
    }
}

CarbonSettingsPanel.template = "sustainability.CarbonSettingsPanel";
CarbonSettingsPanel.components = {CarbonSettings};
CarbonSettingsPanel.props = {
    ...standardWidgetProps,
    types: {type: String},
    options: {type: Object},
};
CarbonSettingsPanel.extractProps = ({attrs}) => {
    return {
        types: attrs.types,
        options: attrs.options,
    };
};
CarbonSettingsPanel.fieldDependencies = {
    carbon_allowed_factor_ids: {
        type: "many2many",
        string: _lt("Carbon allowed factor ids"),
    },

    carbon_in_is_manual: {type: "boolean", string: _lt("Carbon in is manual")},
    carbon_in_mode: {type: "selection", string: _lt("Carbon in mode")},
    carbon_in_factor_id: {type: "many2one", string: _lt("Carbon in Emission Factor")},

    carbon_out_is_manual: {type: "boolean", string: _lt("Carbon in is manual")},
    carbon_out_mode: {
        type: "selection",
        string: _lt("Carbon out mode"),
        selection: [
            ["auto", "Automatic"],
            ["manual", "Manual"],
        ],
    },
    carbon_out_factor_id: {type: "many2one", string: _lt("Carbon out Emission Factor")},
};

registry.category("view_widgets").add("carbon_settings_panel", CarbonSettingsPanel);
