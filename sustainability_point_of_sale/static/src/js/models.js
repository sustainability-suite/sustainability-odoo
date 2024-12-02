/** @odoo-module */

import {patch} from "@web/core/utils/patch";
import {Order, Orderline} from "@point_of_sale/app/store/models";

patch(Order.prototype, {
    export_for_printing() {
        let result = super.export_for_printing(...arguments);

        result.total_carbon_value = this.get_total_carbon_value();

        return result;
    },

    get_total_carbon_value() {
        const total = this.orderlines.reduce((sum, line) => sum + line.carbon_value, 0);
        return Math.round(total * 100) / 100;
    },
});

patch(Orderline.prototype, {
    async setup() {
        super.setup(...arguments);
        this.carbon_value = 0;

        const productId = this.product.id;
        const qty = this.quantity;

        const productRes = await this.env.services.orm.call("product.product", "search_read", [[["id", "=", productId]], ["carbon_out_factor_id"]]);

        if (productRes.length === 0) return;

        const carbonOutFactor = productRes[0].carbon_out_factor_id;

        if (!carbonOutFactor) return;

        const carbonFactor = await this.env.services.orm.call("carbon.factor", "search_read", [[["id", "=", carbonOutFactor[0]]], ["carbon_value"]]);

        if (carbonFactor.length === 0) return;

        const carbonValue = carbonFactor[0].carbon_value || 0;
        this.carbon_value = Math.round(carbonValue * qty * 100) / 100;
    },
    getDisplayData() {
        return {
            ...super.getDisplayData(),
            carbon_value: this.carbon_value,
        };
    },
});
