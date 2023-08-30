import configparser
import db_functions
import tesla_api
import json
import os


def mainfunction(envoy_data=None):
    print('running mainfunction')
    config = configparser.ConfigParser()
    config.read('/etc/enhpaseteslasync/config.ini')
    print(f"charge mode is set to {config['DEFAULT']['charge_mode']}")
    # If charge mode is set to grid don't do anything
    if config['DEFAULT']['charge_mode'] == 'grid':
        print(
            f"charge mode is set to {config['DEFAULT']['charge_mode']} so not doing anything")
        return
    token = os.getenv('TESLAMATEAPI_TOKEN')
    teslamateapi_host = os.getenv('TESLAMATEAPI_HOST')
    teslamateapi_port = os.getenv('TESLAMATEAPI_PORT')
    carid = os.getenv('CARID', '1')
    teslamate_response = tesla_api.get_tesla_status(
        carid, teslamateapi_host, teslamateapi_port)
    if tesla_api.is_car_home(teslamate_response):
        if tesla_api.is_car_plugged_in(teslamate_response):
            battery_level = tesla_api.get_battery_level(teslamate_response)
            # low battery charge no matter what
            if battery_level < int(config['DEFAULT']['minimum_battery_level']):
                tesla_api.set_charging_amps(token, int(
                    config['DEFAULT']['max_amps']), teslamate_response, carid, teslamateapi_host, teslamateapi_port)
                tesla_api.start_charge(
                    token, teslamate_response, carid, teslamateapi_host, teslamateapi_port)
            # high battery stop charging
            elif battery_level > int(config['DEFAULT']['max_battery_level']):
                tesla_api.stop_charge(
                    token, teslamate_response, carid, teslamateapi_host, teslamateapi_port)
            else:
                # car already charging
                if tesla_api.is_car_charging(teslamate_response):
                    current_amps = tesla_api.get_current_amps(
                        teslamate_response)
                    if current_amps is None:
                        print("couldnt get current amps not doing anything")
                        return
                    current_car_consumption = current_amps * \
                        int(config['DEFAULT']['voltage'])
                    if envoy_data is None:
                        envoy_data = db_functions.read_envoy_data_from_db()
                    rest_house_consuption = envoy_data['consumption'] - \
                        current_car_consumption
                    if (rest_house_consuption) > envoy_data['production']:
                        print('house is using too much power stop charge')
                        tesla_api.stop_charge(
                            token, teslamate_response, carid, teslamateapi_host, teslamateapi_port)
                    elif envoy_data['surplus'] > 250:
                        print('still surplus left increase amps')
                        print(json.dumps(envoy_data))
                        new_amps = tesla_api.calculate_increase_amps(
                            envoy_data['surplus'], current_amps)
                        tesla_api.set_charging_amps(
                            token, new_amps, teslamate_response, carid, teslamateapi_host, teslamateapi_port)
                        tesla_api.start_charge(
                            token, teslamate_response, carid, teslamateapi_host, teslamateapi_port)
                    elif envoy_data['surplus'] <= 0:
                        print('negetive surplus lets lower amps')
                        print(json.dumps(envoy_data))
                        new_amps = tesla_api.calculate_decrease_amps(
                            envoy_data['surplus'], current_amps)
                        print(f"lowering amps to {new_amps}")
                        tesla_api.set_charging_amps(
                            token, new_amps, teslamate_response, carid, teslamateapi_host, teslamateapi_port)
                        tesla_api.start_charge(
                            token, teslamate_response, carid, teslamateapi_host, teslamateapi_port)
                    else:
                        print('everything is balanced not doing anything')
                else:  # car not charging
                    if envoy_data is None:
                        envoy_data = db_functions.read_envoy_data_from_db()
                    if envoy_data['surplus'] > int(config['DEFAULT']['minimum_watt']):
                        required_amps = tesla_api.calculate_required_amps(
                            envoy_data['surplus'])
                        tesla_api.set_charging_amps(
                            token, required_amps, teslamate_response, carid, teslamateapi_host, teslamateapi_port)
                        tesla_api.start_charge(
                            token, teslamate_response, carid, teslamateapi_host, teslamateapi_port)
                    else:
                        print('surplus too low not doing anything')
                        print(json.dumps(envoy_data))
        else:
            print('car is not plugged in')
            print(teslamate_response['charging_state'])
    else:
        print('Car is not home, not doing anything')
        print(teslamate_response['location'])
