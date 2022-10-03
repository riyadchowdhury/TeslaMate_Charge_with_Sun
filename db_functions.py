import asyncio
import json
import datetime
import os
import local_envoy_reader
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

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
    url='http://envoyyaml-influxdb-1:8086'
    token='abc123'
    org='teslaorg'
    bucket='teslabucket'
    print('Writing')
    client = influxdb_client.InfluxDBClient(
       url=url,
       token=token,
       org=org
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)
    production_point = influxdb_client.Point("envoy_data").tag("type", "production").field("watt", envoy_data['production'])
    consumption_point = influxdb_client.Point("envoy_data").tag("type", "consumption").field("watt", envoy_data['consumption'])
    surplus_point = influxdb_client.Point("envoy_data").tag("type", "surplus").field("watt", envoy_data['surplus'])
    write_api.write(bucket, org, [production_point, consumption_point, surplus_point])
    print(json.dumps(envoy_data))
    print('Done write')

def read_envoy_data_from_db():
    print('Reading')
    p = {"_start": datetime.timedelta(hours=-1),
     "_type": "production",
     "_every": datetime.timedelta(minutes=5)
     }

    tables = query_api.query('''
        from(bucket:"my-bucket") |> range(start: _start)
            |> filter(fn: (r) => r["_measurement"] == "envoy_data")
            |> filter(fn: (r) => r["_field"] == "watt")
            |> filter(fn: (r) => r["type"] == _type
            |> aggregateWindow(every: _every, fn: mean, createEmpty: true)
    ''', params=p)

    for table in tables:
        print(table)
        for record in table.records:
            print(str(record["_time"]) + " - " + record["type"] + ": " + str(record["_value"]))
            return str(record["_time"]) + " - " + record["type"] + ": " + str(record["_value"])
