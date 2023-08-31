import db
import enphase_api
import json
import os
import datetime


def get_config_from_db():
    database = db.Database()
    database.connect()
    database.execute_query("SELECT * FROM charge_with_sun_settings")
    query_response = database.fetch_one()
    if query_response is not None:
        config_values = {
            "charge_mode": query_response[0],
            "minimum_battery_level": query_response[1],
            "max_amps":  query_response[2],
            "max_battery_level": query_response[3],
            "voltage": query_response[4],
            "minimum_watt": query_response[5]
        }
    else:
        # Default value is DB doesnt have what we need
        config_values = {
            "charge_mode": "solar",
            "minimum_battery_level": 30,
            "max_amps": 32,
            "max_battery_level": 80,
            "voltage": 238,
            "minimum_watt": 500
        }
    database.close()
    return config_values


def save_config_to_db(config):
    database = db.Database()
    database.connect()
    database.execute_query(f"""
                           UPDATE charge_with_sun_settings
                           SET charge_mode = '{config['charge_mode']}', 
                               minimum_battery_level = '{config['minimum_battery_level']}',
                               max_amps = '{config['max_amps']}',
                               max_battery_level = '{config['max_battery_level']}',
                               voltage = '{config['voltage']}',
                               minimum_watt = '{config['minimum_watt']}'
                           """)
    database.close()


def write_envoy_data_to_db():
    database = db.Database()
    database.connect()
    enphase = enphase_api.Enhase()
    envoy_data = enphase.get_envoy_data()
    database.execute_query('''INSERT INTO solar (
                              production, consumption, surplus)
                              VALUES (%s, %s, %s)''',
                           (envoy_data['production'], envoy_data['consumption'], envoy_data['surplus']))
    print(json.dumps(envoy_data))
    print('Done write')
    database.close()
    return envoy_data


def read_envoy_data_from_db():
    print('Reading')
    fiveminsago = datetime.datetime.utcnow() - datetime.timedelta(minutes=20)
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
        return envoy_data
    else:
        data = {
            "production": int(query_result[0]),
            "consumption": int(query_result[1]),
            "surplus": int(query_result[2])
        }
        return data
