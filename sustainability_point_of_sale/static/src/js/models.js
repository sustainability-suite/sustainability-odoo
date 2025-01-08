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
        const total = this.orderlines.reduce(
            (sum, line) => sum + line.carbon_value * line.quantity,
            0
        );
        if (total) return total.toFixed(2);
        return 0;
    },
});

patch(Orderline.prototype, {
    async setup() {
        await super.setup(...arguments);
        await this._setCarbonValue();
    },
    /**
     * Retrieves the product's carbon output factor from the product or its template and sets the `carbon_value`.
     * The standard retrieval hierarchy (product -> template -> category -> company) is bypassed to ensure greater precision for the POS.
     * If the carbon factor is not found in the product or template, the value (0) won't be shown.
     */
    async _setCarbonValue() {
        this.carbon_value = 0;

        const productId = this.product.id;
        productQuantities[productId] = (productQuantities[productId] || 0) + 1;

        const productRes = await this.env.services.orm.searchRead(
            "product.product",
            [["id", "=", productId]],
            ["carbon_out_factor_id", "product_tmpl_id"]
        );
        if (productRes.length === 0) return;

        let carbonOutFactor = productRes[0].carbon_out_factor_id;

        if (!carbonOutFactor) {
            const productTemplate = productRes[0].product_tmpl_id;
            const productTemplateRes = await this.env.services.orm.searchRead(
                "product.template",
                [["id", "=", productTemplate[0]]],
                ["carbon_out_factor_id"]
            );

            if (productTemplateRes.length === 0) return;

            carbonOutFactor = productTemplateRes[0].carbon_out_factor_id;
        }

        if (!carbonOutFactor) return;

        const carbonFactor = await this.env.services.orm.searchRead(
            "carbon.factor",
            [["id", "=", carbonOutFactor[0]]],
            ["carbon_value"]
        );
        if (carbonFactor.length === 0) return;

        this.carbon_value = parseFloat(carbonFactor[0].carbon_value || 0).toFixed(2);
    },
    getDisplayData() {
        const qty = productQuantities[this.product.id];
        const data = super.getDisplayData();

        if (this.carbon_value) data.carbon_value = (this.carbon_value * qty).toFixed(2);

        return data;
    },
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        const productId = json.product_id;
        productQuantities[productId] = json.qty;
        return json;
    },
});
