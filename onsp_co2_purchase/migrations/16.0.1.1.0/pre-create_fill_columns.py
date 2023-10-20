def migrate(cr, version):
    if not version:
        return

    cr.execute(
        """
        ALTER TABLE purchase_order_line
        ADD COLUMN carbon_origin_name character varying,
        ADD COLUMN carbon_origin_value character varying;
        """
    )

    queries = []
    cr.execute("SELECT id, carbon_value_origin FROM purchase_order_line WHERE carbon_value_origin IS NOT NULL AND carbon_value_origin!='';")
    for row in cr.fetchall():
        origin_vals = row[1].split("|")
        if len(origin_vals) == 2:
            name = origin_vals[0]
            value = origin_vals[1]
        else:
            name = row[1]
            value = '0.0'

        queries.append(f"UPDATE purchase_order_line SET carbon_origin_name='{name}', carbon_origin_value='{value}' WHERE id={row[0]}")

    cr.execute(";".join(queries))

