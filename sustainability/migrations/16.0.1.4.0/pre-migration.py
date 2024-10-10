from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(
        env.cr,
        [("carbon.factor.source", "carbon.factor.database")],
    )
    openupgrade.rename_tables(
        env.cr,
        [("carbon_factor_source", "carbon_factor_database")],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_model_fields
        SET name = 'carbon_database_id'
        WHERE name = 'carbon_source_id'
        AND model = 'carbon.factor';
        """,
    )
    openupgrade.rename_fields(
        env,
        [
            (
                "carbon.factor",
                "carbon_factor",
                "carbon_source_id",
                "carbon_database_id",
            ),
        ],
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "sustainability.carbon_factor_source_ademe",
                "sustainability.carbon_factor_database_ademe",
            ),
            (
                "sustainability.carbon_factor_source_other",
                "sustainability.carbon_factor_database_other",
            ),
        ],
    )
