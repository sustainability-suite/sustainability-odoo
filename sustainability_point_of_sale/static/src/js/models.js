/** @odoo-module */

import {Orderline} from "@point_of_sale/app/generic_components/orderline/orderline";
import {PosOrder} from "@point_of_sale/app/models/pos_order";
import {PosOrderline} from "@point_of_sale/app/models/pos_order_line";
import {patch} from "@web/core/utils/patch";

let productQuantities = {};

patch(PosOrder.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.total_carbon_value = this.get_total_carbon_value();
        productQuantities = {};
        return result;
    },

    get_total_carbon_value() {
        const total = this.lines.reduce(
            (sum, line) => sum + line.carbon_value * line.get_quantity(),
            0
        );
        return total ? total.toFixed(2) : 0;
    },
});

patch(PosOrderline.prototype, {
    setup() {
        super.setup(...arguments);
        this.carbon_value = 0;
        this._carbonValueCalculated = false;
        this._setCarbonValue();
    },

    _setCarbonValue() {
        const productId = this.product_id.id;
        productQuantities[productId] = (productQuantities[productId] || 0) + 1;

        if (
            this.product_id.carbon_out_factor_id &&
            this.product_id.carbon_out_factor_id.carbon_value
        ) {
            this.carbon_value = this.product_id.carbon_out_factor_id.carbon_value;
        } else {
            this.carbon_value = 0;
        }
    },

    getDisplayData() {
        const data = super.getDisplayData();
        const qty = productQuantities[this.product_id.id] || this.get_quantity();
        const carbonTotal = parseFloat(this.carbon_value) * qty;

        if (carbonTotal > 0) {
            data.carbon_value = carbonTotal.toFixed(2);
        }

        return data;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        productQuantities[json.product_id] = json.qty;
        return json;
    },
});

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                carbon_value: {type: String, optional: true},
            },
        },
    },
});
