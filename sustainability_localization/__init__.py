# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

_logger = logging.getLogger(__name__)


def update_chart_of_accounts(env, account_to_factor_mapping):
    """Update Chart of Accounts based on account-to-factor mapping using XML IDs."""
    for account_account_ref, carbon_factor_ref in account_to_factor_mapping.items():
        try:
            account = env.ref(account_account_ref)
            carbon_factor = env.ref(carbon_factor_ref)
            if account:
                account.write(
                    {
                        "carbon_in_is_manual": True,
                        "carbon_in_factor_id": carbon_factor.id,
                    }
                )
        except ValueError:
            _logger.warning(
                f"Account or factor with external id '{account_account_ref}' or '{carbon_factor_ref}' not found."
            )


def post_init_hook(env):
    mapping = {
        "account.1_current_assets": "sustainability.carbon_factor_1",
    }

    update_chart_of_accounts(env, mapping)
