# Module db.py
import envoy_reader_module
import asyncio
import os


class Enhase:
    def __init__(self):
        envoy_host = os.getenv('ENVOY_HOST')
        enlighten_user = os.getenv('ENLIGHTEN_USER')
        enlighten_pass = os.getenv('ENLIGHTEN_PASS')
        enlighten_commissioned = os.getenv('ENLIGHTEN_COMISSIONED')
        enlighten_commissioned = os.getenv(
            "ENLIGHTEN_COMISSIONED", 'True').lower() in ('true', '1', 't')
        enlighten_site_id = os.getenv('ENLIGHTEN_SITE_ID')
        enlighten_serial_num = os.getenv('ENLIGHTEN_SERIAL_NUM')

        self.envoy_host = envoy_host
        self.enlighten_user = enlighten_user
        self.enlighten_pass = enlighten_pass
        self.enlighten_commissioned = enlighten_commissioned
        self.enlighten_site_id = enlighten_site_id
        self.enlighten_serial_num = enlighten_serial_num

    def get_envoy_data(self):
        print('getting envoy data')
        envoyreader = envoy_reader_module.EnvoyReader(
            self.envoy_host,
            '',
            inverters=True,
            enlighten_user=self.enlighten_user,
            enlighten_pass=self.enlighten_pass,
            commissioned=self.enlighten_commissioned,
            enlighten_site_id=self.enlighten_site_id,
            enlighten_serial_num=self.enlighten_serial_num,
            https_flag='s',
        )
        asyncio.run(envoyreader.getData())
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
