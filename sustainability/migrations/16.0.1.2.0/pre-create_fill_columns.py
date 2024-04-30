def migrate(cr, version):
    if not version:
        return

    cr.execute(
        """
        ALTER TABLE account_move_line
        ADD COLUMN carbon_origin_name character varying,
        ADD COLUMN carbon_origin_value character varying;
        """
    )

    cr.execute(
        """
        UPDATE account_move_line
        SET
            carbon_origin_name = CASE
                WHEN POSITION('|' IN carbon_value_origin) > 0
                THEN LEFT(carbon_value_origin, POSITION('|' IN carbon_value_origin) - 1)
                ELSE carbon_value_origin
            END,
            carbon_origin_value = CASE
                WHEN POSITION('|' IN carbon_value_origin) > 0
                THEN RIGHT(carbon_value_origin, LENGTH(carbon_value_origin) - POSITION('|' IN carbon_value_origin))
                ELSE '0.0'
        END
        WHERE
            carbon_value_origin IS NOT NULL
            AND carbon_value_origin != '';
    """
    )
