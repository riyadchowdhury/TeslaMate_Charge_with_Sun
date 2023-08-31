import db


def initialize_db():
    database = db.Database()
    database.connect()
    database.execute_query(
        "select exists(select * from information_schema.tables where table_name=%s)", ('charge_with_sun_settings',))
    settings_db_exists = database.fetch_one()[0]
    print(settings_db_exists)
    if not settings_db_exists:
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
    database.execute_query(
        "select exists(select * from information_schema.tables where table_name=%s)", ('solar',))
    solar_db_exists = database.fetch_one()[0]
    if not solar_db_exists:
        print('creating solar db')
        database.execute_query('''CREATE TABLE IF NOT EXISTS solar(
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            production INT,
            consumption INT,
            surplus INT
        )''')
    database.close()
