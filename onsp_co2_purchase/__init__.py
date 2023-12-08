from . import models


def add_carbon_mode_columns(cr):
    """
    We need this pre_init_hook to avoid performance issues on large databases
    """
    cr.execute(
        """
        ALTER TABLE res_partner
        ADD COLUMN carbon_in_mode character varying,
        ADD COLUMN carbon_out_mode character varying;
        """
    )
    cr.execute(
        """
        UPDATE res_partner
        SET carbon_in_mode = 'auto', carbon_out_mode = 'auto'
        """
    )
