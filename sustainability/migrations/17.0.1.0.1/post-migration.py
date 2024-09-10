def migrate(cr, version):
    cr.execute("UPDATE carbon_factor SET carbon_database_id=temp_source_id")
    cr.execute("ALTER TABLE carbon_factor DROP COLUMN temp_source_id")
    cr.execute("UPDATE carbon_line_origin SET factor_database_id=temp_source_id")
    cr.execute("ALTER TABLE carbon_line_origin DROP COLUMN temp_source_id")
    cr.execute("DELETE FROM ir_model_data WHERE model = 'carbon.factor.source'")
