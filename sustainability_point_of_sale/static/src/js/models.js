/** @odoo-module */

import {patch} from "@web/core/utils/patch";
import {Order, Orderline} from "@point_of_sale/app/store/models";

patch(Order.prototype, {
    /**
     * Calculate the total carbon emission factor and add it to the printed receipt.
     */
    export_for_printing() {
        let result = super.export_for_printing(...arguments);

        result.total_carbon_factor = this.get_total_carbon_factor();
        result.order_lines = this.get_order_lines_carbon_factors();

        return result;
    },

    /**
     * Get the total emission factor for the entire order
     */
    get_total_carbon_factor() {
        const total = this.orderlines.reduce((sum, line) => sum + line.carbon_factor, 0);
        return Math.round(total * 100) / 100;
    },
    /**
     * Get emission factor for each order line
     */
    get_order_lines_carbon_factors() {
        return this.orderlines.map((line) => ({
            product_name: line.product.display_name,
            carbon_factor: line.carbon_factor,
        }));
    },
});

patch(Orderline.prototype, {
    async setup() {
        super.setup(...arguments);

        try {
            const productId = this.product.id;
            const qty = this.quantity;

            const productRes = await this.env.services.orm.call("product.product", "search_read", [[["id", "=", productId]], ["carbon_out_factor_id"]]);

            if (productRes.length === 0) {
                this.carbon_factor = 0;
                return;
            }

            const carbonOutFactor = productRes[0].carbon_out_factor_id;

            if (!carbonOutFactor) {
                this.carbon_factor = 0;
                return;
            }

            const carbonFactorRes = await this.env.services.orm.call("carbon.factor", "search_read", [[["id", "=", carbonOutFactor[0]]], ["carbon_value"]]);

            if (carbonFactorRes.length === 0) {
                this.carbon_factor = 0;
                return;
            }

            const carbonValue = carbonFactorRes[0].carbon_value || 0;
            this.carbon_factor = Math.round(carbonValue * qty * 100) / 100;
        } catch (error) {
            this.carbon_factor = 0;
        }
    },
});
