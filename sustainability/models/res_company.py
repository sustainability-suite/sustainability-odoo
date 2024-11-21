from odoo import api, fields, models


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "carbon.mixin"]

    @api.model
    def _get_available_carbon_compute_methods(self) -> list[tuple[str, str]]:
        return [
            ("monetary", "Monetary"),
        ]

    carbon_in_is_manual = fields.Boolean(default=True)
    carbon_out_is_manual = fields.Boolean(default=True)
    carbon_default_data_uncertainty_percentage = fields.Float(default=0.0)

    invoice_report_footer = fields.Html(translate=True)
    carbon_lock_date = fields.Date(
        string="CO2e Computation Lock Date",
        tracking=True,
        help="",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "currency_id" in vals:
                currency = self.env["res.currency"].browse(vals["currency_id"])
                factor_name = f"Global Emission Factor Fallback {currency.name}"
            else:
                factor_name = "Global Emission Factor Fallback"

            carbon_factor = self.env["carbon.factor"].search(
                [("name", "=", factor_name)], limit=1
            )

            if not carbon_factor:
                carbon_factor = self.env["carbon.factor"].create(
                    {
                        "name": factor_name,
                        "carbon_compute_method": "monetary",
                        "uncertainty_percentage": 2,
                        "value_ids": [
                            (
                                0,
                                0,
                                {
                                    "carbon_value": 10.0,
                                    "carbon_monetary_currency_id": currency.id,
                                    "date": "2000-01-01",
                                },
                            ),
                        ],
                    }
                )
            vals["carbon_in_factor_id"] = carbon_factor.id
            vals["carbon_out_factor_id"] = carbon_factor.id
            vals["carbon_in_is_manual"] = True
            vals["carbon_out_is_manual"] = True

        return super().create(vals_list)

    @api.depends("currency_id")
    def _compute_carbon_currencies(self):
        for company in self:
            company.carbon_in_monetary_currency_id = company.currency_id
            company.carbon_out_monetary_currency_id = company.currency_id
