/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { _lt } from "@web/core/l10n/translation";

import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { CarbonSettings} from "@onsp_co2/owl/carbon_settings/carbon_settings";


export class CarbonSettingsPanel extends Component {
    setup() {
        super.setup();
        this.carbon_types = this.props.types.split(',');
    }
    getCarbonTitle(type){
        let options = this.props.options[type];
        return options && 'title' in options ? options.title : '';
    }
}


CarbonSettingsPanel.template = "onsp_co2.CarbonSettingsPanel";
CarbonSettingsPanel.components = { CarbonSettings };
CarbonSettingsPanel.props = {
    ...standardWidgetProps,
    types: { type: String },
    options: { type: Object },
};
CarbonSettingsPanel.extractProps = ({ attrs }) => {
    return {
        types: attrs.types,
        options: attrs.options,
    };
};
CarbonSettingsPanel.fieldDependencies = {
    carbon_currency_label: { type: "string", string: _lt("Carbon currency label") },

    carbon_in_is_manual: { type: "boolean", string: _lt("Carbon in is manual") },
    carbon_in_value: { type: "float", string: _lt("Carbon in value") },
    carbon_in_mode: { type: "selection", string: _lt("Carbon in mode")},
    carbon_in_compute_method: { type: "selection", string: _lt("Carbon in compute method")},
    carbon_in_uom_id: { type: "many2one", string: _lt("Carbon in UOM")},
    carbon_in_monetary_currency_id: { type: "many2one", string: _lt("Carbon in Monetary Currency")},
    carbon_in_factor_id: { type: "many2one", string: _lt("Carbon in Emission Factor")},
    carbon_in_value_origin: { type: "string", string: _lt("Carbon in origin") },

    carbon_out_is_manual: { type: "boolean", string: _lt("Carbon in is manual") },
    carbon_out_value: { type: "float", string: _lt("Carbon out value") },
    carbon_out_mode: { type: "selection", string: _lt("Carbon out mode"), selection: [["auto", "Automatic"], ["manual", "Manual"]] },
    carbon_out_compute_method: { type: "selection", string: _lt("Carbon out compute method")},
    carbon_out_uom_id: { type: "many2one", string: _lt("Carbon out UOM")},
    carbon_out_monetary_currency_id: { type: "many2one", string: _lt("Carbon out Monetary Currency")},
    carbon_out_factor_id: { type: "many2one", string: _lt("Carbon out Emission Factor")},
    carbon_out_value_origin: { type: "string", string: _lt("Carbon out origin") },
};


registry.category("view_widgets").add("carbon_settings_panel", CarbonSettingsPanel);
