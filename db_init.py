import db


def initialize_db():
    database = db.Database()
    database.connect()
    database.execute_query(
        "select exists(select * from information_schema.tables where table_name=%s)", ('charge_with_sun_settings',))
    db_exists = database.fetch_one()[0]
    print(db_exists)
    if not db_exists:
        database.execute_query('''CREATE TABLE IF NOT EXISTS charge_with_sun_settings(
            charge_mode VARCHAR(5),
            minimum_battery_level INT,
            max_amps INT,
            max_battery_level INT,
            voltage INT,
            minimum_watt INT
        )''')
        database.execute_query('''INSERT INTO public.charge_with_sun_settings (
                                  charge_mode, minimum_battery_level, max_amps, max_battery_level, voltage, minimum_watt)
                                  VALUES (%s, %s, %s, %s, %s, %s)''',
                               ('solar', 30, 32, 90, 238, 500))
    database.close()
