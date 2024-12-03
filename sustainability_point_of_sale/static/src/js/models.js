/** @odoo-module */

import {patch} from "@web/core/utils/patch";
import {Order, Orderline} from "@point_of_sale/app/store/models";

let productQuantities = {};

patch(Order.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.total_carbon_value = this.get_total_carbon_value();

        productQuantities = {};

        return result;
    },
    get_total_carbon_value() {
        const total = this.orderlines.reduce((sum, line) => sum + line.carbon_value * line.quantity, 0);
        return total.toFixed(2);
    },
});

patch(Orderline.prototype, {
    async setup() {
        await super.setup(...arguments);
        await this._setCarbonValue();
    },
    async _setCarbonValue() {
        this.carbon_value = 0;

        const productId = this.product.id;
        productQuantities[productId] = (productQuantities[productId] || 0) + 1;

        const productRes = await this.env.services.orm.searchRead("product.product", [["id", "=", productId]], ["carbon_out_factor_id"]);
        if (productRes.length === 0) return;

        const carbonOutFactor = productRes[0].carbon_out_factor_id;
        if (!carbonOutFactor) return;

        const carbonFactor = await this.env.services.orm.searchRead("carbon.factor", [["id", "=", carbonOutFactor[0]]], ["carbon_value"]);
        if (carbonFactor.length === 0) return;

        this.carbon_value = parseFloat(carbonFactor[0].carbon_value || 0).toFixed(2);
    },
    getDisplayData() {
        const qty = productQuantities[this.product.id];
        return {
            ...super.getDisplayData(),
            carbon_value: (this.carbon_value * qty).toFixed(2),
        };
    },
});
