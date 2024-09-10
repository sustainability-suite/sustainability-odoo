def migrate(cr, version):
    cr.execute("ALTER TABLE carbon_factor ADD COLUMN temp_source_id INTEGER")
    cr.execute("UPDATE carbon_factor SET temp_source_id=carbon_source_id")
    cr.execute("ALTER TABLE carbon_line_origin ADD COLUMN temp_source_id INTEGER")
    cr.execute("UPDATE carbon_line_origin SET temp_source_id=factor_source_id")
