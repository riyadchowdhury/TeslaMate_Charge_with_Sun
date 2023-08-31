import db
import asyncio
import json
import datetime
import os
import local_envoy_reader
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

url = os.getenv('INFLUXDB_URL')
token = os.getenv('INFLUXDB_TOKEN')
org = os.getenv('INFLUXDB_ORG')
bucket = os.getenv('INFLUXDB_BUCKET')
client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)


def get_config_from_db():
    database = db.Database()
    database.connect()
    database.execute_query("SELECT * FROM charge_with_sun_settings")
    query_response = database.fetch_one()
    config_values = {
        "charge_mode": query_response[0],
        "minimum_battery_level": query_response[1],
        "max_amps":  query_response[2],
        "max_battery_level": query_response[3],
        "voltage": query_response[4],
        "minimum_watt": query_response[5]
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


def get_envoy_data():
    print('getting envoy data')
    envoy_host = os.getenv('ENVOY_HOST')
    enlighten_user = os.getenv('ENLIGHTEN_USER')
    enlighten_pass = os.getenv('ENLIGHTEN_PASS')
    enlighten_commissioned = os.getenv('ENLIGHTEN_COMISSIONED')
    enlighten_site_id = os.getenv('ENLIGHTEN_SITE_ID')
    enlighten_serial_num = os.getenv('ENLIGHTEN_SERIAL_NUM')
    envoyreader = local_envoy_reader.EnvoyReader(
        envoy_host,
        '',
        inverters=True,
        enlighten_user=enlighten_user,
        enlighten_pass=enlighten_pass,
        commissioned=enlighten_commissioned,
        enlighten_site_id=enlighten_site_id,
        enlighten_serial_num=enlighten_serial_num,
        https_flag='s',
    )
    data_results = asyncio.run(envoyreader.getData())
    production = asyncio.run(envoyreader.production())
    consumption = asyncio.run(envoyreader.consumption())
    surplus = int(production) - int(consumption)
    print(production)
    data = {
        "production": int(production),
        "consumption": int(consumption),
        "surplus": surplus
    }
    return data


def write_envoy_data_to_db():
    envoy_data = get_envoy_data()
    write_api = client.write_api(write_options=SYNCHRONOUS)
    production_point = influxdb_client.Point("envoy_data").tag(
        "type", "production").field("watt", envoy_data['production'])
    consumption_point = influxdb_client.Point("envoy_data").tag(
        "type", "consumption").field("watt", envoy_data['consumption'])
    surplus_point = influxdb_client.Point("envoy_data").tag(
        "type", "surplus").field("watt", envoy_data['surplus'])
    write_api.write(bucket, org, [production_point,
                    consumption_point, surplus_point])
    print(json.dumps(envoy_data))
    print('Done write')
    return envoy_data


def read_envoy_data_from_db():
    print('Reading')
    query_api = client.query_api()
    query = '''
        from(bucket:_bucket)\
            |> range(start: -5m)\
            |> filter(fn:(r) => r._measurement == "envoy_data")\
            |> filter(fn:(r) => r._field == "watt" )
            |> aggregateWindow(every: 5m, fn: mean)
    '''
    param = {
        "_bucket": bucket
    }
    tables = query_api.query(org=org, query=query, params=param)
    data = {}
    for table in tables:
        for record in table.records:
            data[record.values.get("type")] = record.get_value()
    if data['production'] is None or data['consumption'] is None or data['surplus'] is None:
        envoy_data = get_envoy_data()
        return envoy_data
    else:
        return data
