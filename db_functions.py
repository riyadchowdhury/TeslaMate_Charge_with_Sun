import db
import enphase_api
import json
import datetime
import globals
import logging

logger = logging.getLogger(__name__)


def get_config_from_db():
    database = db.Database()
    database.connect()
    database.execute_query("SELECT * FROM charge_with_sun_settings")
    query_response = database.fetch_one()
    if query_response is not None:
        config_values = {
            "charge_mode": query_response[0],
            "minimum_battery_level": query_response[1],
            "voltage": query_response[2],
            "minimum_watt": query_response[3]
        }
    else:
        # Default value is DB doesnt have what we need
        config_values = {
            "charge_mode": "solar",
            "minimum_battery_level": 30,
            "voltage": 238,
            "minimum_watt": 500
        }
    database.close()
    logging.debug('Got config from db: %s', config_values)
    return config_values


def save_config_to_db(config):
    database = db.Database()
    database.connect()
    database.execute_query(f"""
                           UPDATE charge_with_sun_settings
                           SET charge_mode = '{config['charge_mode']}', 
                               minimum_battery_level = '{config['minimum_battery_level']}',
                               voltage = '{config['voltage']}',
                               minimum_watt = '{config['minimum_watt']}'
                           """)
    logging.debug('Saved config to db: %s', config)
    database.close()


def write_envoy_data_to_db():
    database = db.Database()
    database.connect()
    enphase = enphase_api.Enhase()
    envoy_data = enphase.get_envoy_data()
    database.execute_query('''INSERT INTO solar (
                              production, consumption, surplus, charging)
                              VALUES (%s, %s, %s, %s)''',
                           (envoy_data['production'], envoy_data['consumption'], envoy_data['surplus'], globals.charging))
    logging.info('Writing envoy data to db: %s', envoy_data)
    database.close()
    return envoy_data


def read_envoy_data_from_db():
    fiveminsago = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    database = db.Database()
    database.connect()
    database.execute_query(f"""SELECT 
                               AVG(production),AVG(consumption),AVG(surplus) 
                               FROM solar 
                               WHERE timestamp BETWEEN '{fiveminsago}' AND LOCALTIMESTAMP;""")
    query_result = database.fetch_one()
    database.close()
    if query_result is None or query_result[0] is None or query_result[1] is None or query_result[2] is None:
        enphase = enphase_api.Enhase()
        envoy_data = enphase.get_envoy_data()
        logging.warning(
            'Database does not contain enough data, returning current live data: %s', envoy_data)
        return envoy_data
    else:
        data = {
            "production": int(query_result[0]),
            "consumption": int(query_result[1]),
            "surplus": int(query_result[2])
        }
        logging.debug('Average envoy data from last 5 mins: %s', data)
        return data
