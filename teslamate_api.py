import json
import time
import requests
import os
import globals
import logging

logger = logging.getLogger(__name__)


class TeslaMate:
    def __init__(self):
        token = os.getenv('TESLAMATEAPI_TOKEN')
        teslamateapi_host = os.getenv('TESLAMATEAPI_HOST')
        teslamateapi_port = os.getenv('TESLAMATEAPI_PORT')
        carid = os.getenv('CARID', '1')

        self.token = token
        self.teslamateapi_host = teslamateapi_host
        self.teslamateapi_port = teslamateapi_port
        self.carid = carid

        tesla_status = self.get_tesla_status()
        self.tesla_status = tesla_status
        globals.charging = self.is_car_charging()

    def get_tesla_status(self):
        r = requests.get(
            f"http://{self.teslamateapi_host}:{self.teslamateapi_port}/api/v1/cars/{self.carid}/status",
        )
        tesla_status = r.json()
        logging.debug('Tesla Status from TeslaMate: %s', tesla_status)
        return tesla_status

    def set_charging_amps(self, amps, attempt=0):
        if self.tesla_status['data']['status']['state'] == 'asleep' or self.tesla_status['data']['status']['state'] == 'suspended':
            self.wake_car()
            time.sleep(15)
        if amps < 5:  # tesla api does not allow charging less than 5 amps
            amps = 5
        if int(self.tesla_status['data']['status']['charging_details']['charge_current_request']) != amps:
            charging_amps = {'charging_amps': amps}
            r = requests.post(
                f"http://{self.teslamateapi_host}:{self.teslamateapi_port}/api/v1/cars/{self.carid}/command/set_charging_amps",
                json=charging_amps,
                headers={
                    'Authorization': f"Bearer {self.token}"
                }
            )
            logging.debug('Response from API when setting amps: %s', r.content)
            if r.status_code != 200:
                attempt = attempt + 1
                logging.warning(
                    'Couldnt set charge trying again attempt: %s', attempt)
                time.sleep(5)
                if attempt < 3:
                    self.set_charging_amps(amps, attempt)
            else:
                logging.info(f"Car set to {amps} amps")
        else:
            logging.info(f"Car already set to charge at {amps} amps")

    def is_car_plugged_in(self):
        return self.tesla_status['data']['status']['charging_details']['plugged_in']

    def is_car_home(self):
        if self.tesla_status['data']['status']['car_geodata']['geofence'] == 'Home':
            return True
        else:
            return False

    def is_car_charging(self):
        if self.tesla_status['data']['status']['state'] == 'charging':
            return True
        else:
            return False

    def get_battery_level(self):
        return int(self.tesla_status['data']['status']['battery_details']['battery_level'])

    def get_current_amps(self):
        current_amps = int(
            self.tesla_status['data']['status']['charging_details']['charge_current_request'])
        if current_amps < 5:
            current_amps = 5
        return current_amps

    def get_max_amps(self):
        max_amps = int(
            self.tesla_status['data']['status']['charging_details']['charge_current_request_max'])
        return max_amps

    def get_max_soc(self):
        max_soc = int(
            self.tesla_status['data']['status']['charging_details']['charge_limit_soc'])
        return max_soc

    def get_voltage(self, voltagefromconfig):
        voltage = int(
            self.tesla_status['data']['status']['charging_details']['charger_voltage'])
        if voltage < 200:  # Sometimes teslamate returns really low voltage in the API
            voltage = voltagefromconfig
        return voltage

    def start_charge(self):
        if self.tesla_status['data']['status']['state'] != 'charging':
            r = requests.post(
                f"http://{self.teslamateapi_host}:{self.teslamateapi_port}/api/v1/cars/{self.carid}/command/charge_start",
                headers={
                    'Authorization': f"Bearer {self.token}"
                }
            )
            logging.debug('Response from API when setting amps: %s', r.content)
            if r.status_code != 200:
                logging.error(
                    'Couldnt start charge: %s', r.content)
            else:
                logger.info("Started charging")
                globals.charging = True
        else:
            logger.info("Car was already charging")

    def wake_car(self):
        if self.tesla_status['data']['status']['state'] == 'asleep' or self.tesla_status['data']['status']['state'] == 'suspended':
            r = requests.post(
                f"http://{self.teslamateapi_host}:{self.teslamateapi_port}/api/v1/cars/{self.carid}/wake_up",
                headers={
                    'Authorization': f"Bearer {self.token}"
                }
            )
            logging.debug('Response from API when waking car: %s', r.content)
            if r.status_code != 200:
                logging.error(
                    'Couldnt wake cake: %s', r.content)
            else:
                logger.info("Woken car")
        else:
            logger.info("Car was already awake")

    def stop_charge(self):
        if self.tesla_status['data']['status']['state'] == 'charging':
            r = requests.post(
                f"http://{self.teslamateapi_host}:{self.teslamateapi_port}/api/v1/cars/{self.carid}/command/charge_stop",
                headers={
                    'Authorization': f"Bearer {self.token}"
                }
            )
            logging.debug(
                'Response from API when stopping charge: %s', r.content)
            if r.status_code != 200:
                logging.error(
                    'Couldnt stop charge: %s', r.content)
            else:
                logger.info("Stopped charge")
                globals.charging = False
        else:
            logger.info("Car not charging nothing to stop, current state: %s",
                        self.tesla_status['data']['status']['state'])
