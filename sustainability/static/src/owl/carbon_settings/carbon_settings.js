/** @odoo-module **/

import {Component, EventBus} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {_lt} from "@web/core/l10n/translation";

import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";
import {FloatField} from "@web/views/fields/float/float_field";
import {Many2OneField} from "@web/views/fields/many2one/many2one_field";
import {BooleanToggleField} from "@web/views/fields/boolean_toggle/boolean_toggle_field";
import {X2ManyField} from "@web/views/fields/x2many/x2many_field";
import {useService} from "@web/core/utils/hooks";
import {usePopover} from "@web/core/popover/popover_hook";

export class CarbonOriginPopover extends Component {}
CarbonOriginPopover.template = "sustainability.CarbonOriginPopover";

export class CarbonSettings extends Component {
    setup() {
        super.setup();
        this.bus = new EventBus();
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.popover = usePopover();
        this.closePopover = null;
        this.carbonType = "carbon_" + this.props.type;
        // this.availableComputeMethods = this.props.record.fields[this.getCarbonFieldFullName('compute_method')].selection.map((e) =>  e[0]);
    }

    // --- Helpers ---
    getCarbonFieldFullName(name) {
        return this.carbonType + "_" + name;
    }
    getCarbonField(name) {
        return this.props.record.data[this.getCarbonFieldFullName(name)];
    }

    // --- 'Interactive' Methods ---

    async updateMode(ev) {
        await this.props.record.discard();
        await this.props.record.update({
            [this.getCarbonFieldFullName("is_manual")]:
                ev.target.dataset.mode === "manual",
            [this.getCarbonFieldFullName("factor_id")]: false,
        });
        // await this.props.record.save();
    }

    // async updateMethod(ev){
    //     await this.props.record.update({
    //         [this.getCarbonFieldFullName('compute_method')]: ev.target.closest('button').dataset.method,
    //     });
    //     // I don't save immediately to avoid ValidationError
    //     await this.props.record.model.notify();
    // }

    // This method is 'standard' as it's a `Field` method passed as props
    async updateField(newValue) {
        await this.record.update({
            [this.name]: newValue,
        });
        await this.record.model.notify();
    }

    async updateFactor(newValue) {
        // if (newValue !== false) {
        //     let name = this.name.includes("_in") ? "carbon_in_compute_method" : "carbon_out_compute_method";
        //     await this.record.update({
        //         [name]: false,
        //     });
        //
        // }
        await this.record.model.orm.call(
            this.record.resModel,
            "carbon_widget_update_field",
            [[this.record.data.id], this.name, newValue]
        );
        await this.record.model.notify();
    }

    async recomputeCarbon() {
        let res = await this.orm.call(
            this.props.record.resModel,
            "action_recompute_carbon",
            [[this.props.record.data.id], this.carbonType]
        );
        if (res === true) {
            this.notification.add(_lt("Carbon has been recomputed!"), {
                type: "success",
            });
        } else {
            this.notification.add(_lt("An error occurred while recomputing carbon"), {
                type: "danger",
            });
        }
    }

    showOrigin(ev) {
        this.closePopover = this.popover.add(
            ev.currentTarget,
            this.constructor.components.CarbonOriginPopover,
            {
                bus: this.bus,
                record: this.props.record,
                type: this.props.type,
                origin: this.getCarbonField("value_origin"),
            },
            {position: "top"}
        );
        this.bus.addEventListener("close-popover", this.closePopover);
    }
}

CarbonSettings.template = "sustainability.CarbonSettings";
CarbonSettings.components = {
    FloatField,
    Many2OneField,
    BooleanToggleField,
    X2ManyField,
    CarbonOriginPopover,
};
CarbonSettings.props = {
    ...standardWidgetProps,
    type: {type: String},
    title: {type: String, optional: true},
    showDistribution: {type: Boolean, optional: true},
};

registry.category("view_widgets").add("carbon_settings", CarbonSettings);
