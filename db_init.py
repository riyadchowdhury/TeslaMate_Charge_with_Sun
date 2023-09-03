import db
import logging

logger = logging.getLogger(__name__)


def initialize_db():
    database = db.Database()
    database.connect()
    database.execute_query(
        "select exists(select * from information_schema.tables where table_name=%s)", ('charge_with_sun_settings',))
    query_response = database.fetch_one()
    settings_db_exists = False
    if query_response is not None:
        settings_db_exists = query_response[0]
    if not settings_db_exists:
        logging.warning(
            'Settings table does not exist, creating a new table with default values')
        database.execute_query('''CREATE TABLE IF NOT EXISTS charge_with_sun_settings(
            charge_mode VARCHAR(5),
            minimum_battery_level INT,
            voltage INT,
            minimum_watt INT
        )''')
        database.execute_query('''INSERT INTO public.charge_with_sun_settings (
                                  charge_mode, minimum_battery_level, voltage, minimum_watt)
                                  VALUES (%s, %s, %s, %s)''',
                               ('solar', 30, 238, 500))
    database.execute_query(
        "select exists(select * from information_schema.tables where table_name=%s)", ('solar',))
    query_response = database.fetch_one()
    solar_db_exists = False
    if query_response is not None:
        solar_db_exists = query_response[0]
    if not solar_db_exists:
        logging.warning(
            'Enphase data tables does not exist, creating new table')
        database.execute_query('''CREATE TABLE IF NOT EXISTS solar(
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
            production INT,
            consumption INT,
            surplus INT,
            charging BOOLEAN
        )''')
    database.close()
