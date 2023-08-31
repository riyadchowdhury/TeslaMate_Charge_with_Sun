import json
import time
import requests


def get_tesla_status(carid, teslamateapi_host, teslamateapi_port):
    r = requests.get(
        f"http://{teslamateapi_host}:{teslamateapi_port}/api/v1/cars/{carid}/status",
    )
    feed = r.json()
    print(feed)
    return feed


def set_charging_amps(token, amps, teslamate_response, carid, teslamateapi_host, teslamateapi_port, attempt=1):
    if amps < 5:  # tesla api does not allow charging less than 5 amps
        amps = 5
    if int(teslamate_response['data']['status']['charging_details']['charge_current_request']) != amps:
        charging_amps = {'charging_amps': amps}
        r = requests.post(
            f"http://{teslamateapi_host}:{teslamateapi_port}/api/v1/cars/{carid}/command/set_charging_amps",
            json=charging_amps,
            headers={
                'Authorization': f"Bearer {token}"
            }
        )
        print(r.content)
        if r.status_code != 200:
            attempt = attempt + 1
            print("Error setting charge try {attempt}")
            time.sleep(5)
            if attempt < 4:
                wake_car(token, teslamate_response, carid,
                         teslamateapi_host, teslamateapi_port)
                time.sleep(15)
                set_charging_amps(token, amps, teslamate_response,
                                  carid, teslamateapi_host, teslamateapi_port, attempt)
        else:
            print(f"car set to {amps} amps")
    else:
        print(f"car already set to charge at {amps} amps")


def is_car_plugged_in(teslamate_response):
    return teslamate_response['data']['status']['charging_details']['plugged_in']


def is_car_home(teslamate_response):
    if teslamate_response['data']['status']['car_geodata']['geofence'] == 'Home':
        return True
    else:
        return False


def is_car_charging(teslamate_response):
    if teslamate_response['data']['status']['state'] == 'charging':
        return True
    else:
        return False


def get_battery_level(teslamate_response):
    return int(teslamate_response['data']['status']['battery_details']['battery_level'])


def get_current_amps(teslamate_response):
    current_amps = int(
        teslamate_response['data']['status']['charging_details']['charge_current_request'])
    if current_amps < 5:
        current_amps = 5
    return current_amps


def start_charge(token, teslamate_response, carid, teslamateapi_host, teslamateapi_port):
    if teslamate_response['data']['status']['state'] != 'charging':
        r = requests.post(
            f"http://{teslamateapi_host}:{teslamateapi_port}/api/v1/cars/{carid}/command/charge_start",
            headers={
                'Authorization': f"Bearer {token}"
            }
        )
        print(r.content)
        if r.status_code != 200:
            print("Error setting charge")
        else:
            print("starting charge")
    else:
        print('car already charging')


def wake_car(token, teslamate_response, carid, teslamateapi_host, teslamateapi_port):
    if teslamate_response['data']['status']['state'] == 'asleep':
        r = requests.post(
            f"http://{teslamateapi_host}:{teslamateapi_port}/api/v1/cars/{carid}/wake_up",
            headers={
                'Authorization': f"Bearer {token}"
            }
        )
        print(r.content)
        if r.status_code != 200:
            print("Error waking car")
        else:
            print("waking charge")
    else:
        print('car already awake')


def stop_charge(token, teslamate_response, carid, teslamateapi_host, teslamateapi_port):
    if teslamate_response['data']['status']['state'] == 'charging':
        r = requests.post(
            f"http://{teslamateapi_host}:{teslamateapi_port}/api/v1/cars/{carid}/command/charge_stop",
            headers={
                'Authorization': f"Bearer {token}"
            }
        )
        print(r.content)
        if r.status_code != 200:
            print("Error setting charge")
        else:
            print("stopping charge")
    else:
        print('car not charging nothing to stop, current state ' +
              teslamate_response['data']['status']['state'])


def calculate_required_amps(surplus):
    amps = surplus // 238
    if amps < 32:
        return amps
    else:
        return 32


def calculate_increase_amps(surplus, current_car_amps):
    amps = surplus // 238
    new_amps = amps + current_car_amps
    if new_amps < 32:
        return int(new_amps)
    else:
        return 32


def calculate_decrease_amps(surplus, current_car_amps):
    amps = abs(surplus) // 238
    new_amps = current_car_amps - amps
    if new_amps < 0:
        return 0
    else:
        return int(new_amps)
