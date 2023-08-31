import db_functions
import teslamate_api
import calculate_amps
import json
import os


def mainfunction(envoy_data=None):
    print('running mainfunction')
    config = db_functions.get_config_from_db()
    print(f"charge mode is set to {config['charge_mode']}")
    # If charge mode is set to grid don't do anything
    if config['charge_mode'] == 'grid':
        print(
            f"charge mode is set to {config['charge_mode']} so not doing anything")
        return
    token = os.getenv('TESLAMATEAPI_TOKEN')
    teslamateapi_host = os.getenv('TESLAMATEAPI_HOST')
    teslamateapi_port = os.getenv('TESLAMATEAPI_PORT')
    carid = os.getenv('CARID', '1')
    teslamate = teslamate_api.TeslaMate()
    tesla_status = teslamate.get_tesla_status()
    if teslamate.is_car_home():
        if teslamate.is_car_plugged_in():
            battery_level = teslamate.get_battery_level()
            # low battery charge no matter what
            if battery_level < int(config['minimum_battery_level']):
                teslamate.set_charging_amps(int(config['max_amps']))
                teslamate.start_charge()
            # high battery stop charging
            elif battery_level > int(config['max_battery_level']):
                teslamate.stop_charge()
            else:
                # car already charging
                if teslamate.is_car_charging():
                    current_amps = teslamate.get_current_amps()
                    if current_amps is None:
                        print("couldnt get current amps not doing anything")
                        return
                    current_car_consumption = current_amps * \
                        int(config['voltage'])
                    if envoy_data is None:
                        envoy_data = db_functions.read_envoy_data_from_db()
                    rest_house_consuption = envoy_data['consumption'] - \
                        current_car_consumption
                    if (rest_house_consuption) > envoy_data['production']:
                        print('house is using too much power stop charge')
                        teslamate.stop_charge()
                    elif envoy_data['surplus'] > 250:
                        print('still surplus left increase amps')
                        print(json.dumps(envoy_data))
                        new_amps = calculate_amps.calculate_increase_amps(
                            envoy_data['surplus'], current_amps, config['voltage'])
                        teslamate.set_charging_amps(new_amps)
                        teslamate.start_charge()
                    elif envoy_data['surplus'] <= 0:
                        print('negetive surplus lets lower amps')
                        print(json.dumps(envoy_data))
                        new_amps = calculate_amps.calculate_decrease_amps(
                            envoy_data['surplus'], current_amps, config['voltage'])
                        print(f"lowering amps to {new_amps}")
                        teslamate.set_charging_amps(new_amps)
                        teslamate.start_charge()
                    else:
                        print('everything is balanced not doing anything')
                else:  # car not charging
                    if envoy_data is None:
                        envoy_data = db_functions.read_envoy_data_from_db()
                    if envoy_data['surplus'] > int(config['minimum_watt']):
                        required_amps = calculate_amps.calculate_required_amps(
                            envoy_data['surplus'], config['voltage'])
                        teslamate.set_charging_amps(required_amps)
                        teslamate.start_charge()
                    else:
                        print('surplus too low not doing anything')
                        print(json.dumps(envoy_data))
        else:
            print('car is not plugged in')
    else:
        print('Car is not home, not doing anything')
