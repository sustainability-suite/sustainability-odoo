from . import models


def add_carbon_mode_columns(env):
    if (
        "carbon_in_mode" in env["res.partner"]._fields
        and "carbon_out_mode" in env["res.partner"]._fields
    ):
        return

    """
    We need this pre_init_hook to avoid performance issues on large databases
    """
    env.cr.execute(
        """
        ALTER TABLE res_partner
        ADD COLUMN IF NOT EXISTS carbon_in_mode character varying,
        ADD COLUMN IF NOT EXISTS carbon_out_mode character varying;
        """
    )
    env.cr.execute(
        """
        UPDATE res_partner
        SET carbon_in_mode = 'auto', carbon_out_mode = 'auto'
        """
    )
