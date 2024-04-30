from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    for company in env["res.company"].search([]):
        company_factor = env["carbon.factor"].create(
            {
                "name": "[MIG] Company Factor for %s" % company.name,
                "carbon_compute_method": "monetary",
                "value_ids": [
                    (
                        0,
                        0,
                        {
                            "date": "1970-01-01",
                            "carbon_value": 0.22,
                            "carbon_monetary_currency_id": company.currency_id.id,
                        },
                    )
                ],
            }
        )
        company.write(
            {
                "carbon_in_is_manual": True,
                "carbon_out_is_manual": True,
                "carbon_in_factor_id": company_factor.id,
                "carbon_out_factor_id": company_factor.id,
            }
        )
