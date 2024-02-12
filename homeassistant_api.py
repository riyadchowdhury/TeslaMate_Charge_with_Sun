# Module db.py
import asyncio
import os
import logging
import requests

logger = logging.getLogger(__name__)


class HomeAssistantEnvoy:
    def __init__(self):
        ha_host = os.getenv('HOMEASSISTANT_HOST')
        ha_port = os.getenv('HOMEASSISTANT_PORT')
        ha_api_key = os.getenv('HOMEASSISTANT_API_KEY')
        ha_serial_num = os.getenv('HOMEASSISTANT_SERIAL_NUM')

        self.ha_host = ha_host
        self.ha_port = ha_port
        self.ha_api_key = ha_api_key
        self.ha_serial_num = ha_serial_num

    def get_envoy_data_from_ha(self):
        r_consumption = requests.get(
            f"http://{self.ha_host}:{self.ha_port}/api/states/sensor.envoy_{self.ha_serial_num}_current_power_consumption",
            headers={
                'Authorization': f"Bearer {self.ha_api_key}",
                'Content-Type': 'application/json'
            }
        )
        consumption_multiplier = 1
        current_power_consumption = r_consumption.json()
        if current_power_consumption['attributes']['unit_of_measurement'] == 'kW':
            consumption_multiplier = 1000
        elif current_power_consumption['attributes']['unit_of_measurement'] == 'MW':
            consumption_multiplier = 1000 * 1000
        consumption = float(
            current_power_consumption['state']) * consumption_multiplier
        r_production = requests.get(
            f"http://{self.ha_host}:{self.ha_port}/api/states/sensor.envoy_{self.ha_serial_num}_current_power_production",
            headers={
                'Authorization': f"Bearer {self.ha_api_key}",
                'Content-Type': 'application/json'
            }
        )
        production_multiplier = 1
        current_power_production = r_production.json()
        if current_power_production['attributes']['unit_of_measurement'] == 'kW':
            production_multiplier = 1000
        elif current_power_production['attributes']['unit_of_measurement'] == 'MW':
            production_multiplier = 1000 * 1000
        production = float(
            current_power_production['state']) * production_multiplier
        surplus = int(production) - int(consumption)
        data = {
            "production": int(production),
            "consumption": int(consumption),
            "surplus": surplus
        }
        logging.debug('Got data from ha envoy device: %s', data)
        return data
