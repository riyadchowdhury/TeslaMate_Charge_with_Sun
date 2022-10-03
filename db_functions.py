import asyncio
import json
import datetime
import os
import local_envoy_reader
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

url=os.getenv('INFLUXDB_URL')
token=os.getenv('INFLUXDB_TOKEN')
org=os.getenv('INFLUXDB_ORG')
bucket=os.getenv('INFLUXDB_BUCKET')
client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

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
    production_point = influxdb_client.Point("envoy_data").tag("type", "production").field("watt", envoy_data['production'])
    consumption_point = influxdb_client.Point("envoy_data").tag("type", "consumption").field("watt", envoy_data['consumption'])
    surplus_point = influxdb_client.Point("envoy_data").tag("type", "surplus").field("watt", envoy_data['surplus'])
    write_api.write(bucket, org, [production_point, consumption_point, surplus_point])
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
    return data
