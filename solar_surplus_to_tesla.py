import db_functions
import tesla_api
import json
import os

def mainfunction(envoy_data=None):
    print('running mainfunction')
    token = os.getenv('TESLAFI_API')
    teslafi_dict = tesla_api.get_tesla_feed(token)
    if tesla_api.is_car_home(teslafi_dict):
        if tesla_api.is_car_plugged_in(token, teslafi_dict):
            battery_level = tesla_api.get_battery_level(teslafi_dict)
            if battery_level < 30: #low battery charge no matter what
                tesla_api.set_charging_amps(token, 32, teslafi_dict)
                tesla_api.start_charge(token, teslafi_dict)
            elif battery_level > 90: # high battery stop charging
                tesla_api.stop_charge(token, teslafi_dict)
            else:
                if tesla_api.is_car_charging(teslafi_dict): #car already charging
                    current_amps = tesla_api.get_current_amps(teslafi_dict)
                    current_car_consumption = current_amps * 238
                    if envoy_data is None:
                        envoy_data = db_functions.read_envoy_data_from_db()
                    rest_house_consuption = envoy_data['consumption'] - current_car_consumption
                    if (rest_house_consuption + 500) > envoy_data['production']:
                        print('house is using too much power stop charge')
                        tesla_api.stop_charge(token, teslafi_dict)
                    elif envoy_data['surplus'] > 250:
                        print('still surplus left increase amps')
                        print(json.dumps(envoy_data))
                        new_amps = tesla_api.calculate_increase_amps(envoy_data['surplus'], current_amps)
                        tesla_api.set_charging_amps(token, new_amps, teslafi_dict)
                        tesla_api.start_charge(token, teslafi_dict)
                    elif envoy_data['surplus'] <= 0:
                        print('negetive surplus lets lower amps')
                        print(json.dumps(envoy_data))
                        new_amps = tesla_api.calculate_decrease_amps(envoy_data['surplus'], current_amps)
                        if new_amps == 0:
                            print('need to lower amps to 0, so stopping charge')
                            tesla_api.stop_charge(token, teslafi_dict)
                        else:
                            print(f"lowering amps to {new_amps}")
                            tesla_api.set_charging_amps(token, new_amps, teslafi_dict)
                            tesla_api.start_charge(token, teslafi_dict)
                    else:
                        print('everything is balanced not doing anything')
                else: #car not charging
                    if envoy_data is None:
                        envoy_data = db_functions.read_envoy_data_from_db()
                    print(json.dumps(envoy_data))
                    if envoy_data['surplus'] > 500:
                        required_amps = tesla_api.calculate_required_amps(envoy_data['surplus'])
                        tesla_api.set_charging_amps(token, required_amps, teslafi_dict)
                        tesla_api.start_charge(token, teslafi_dict)
                    else:
                        print('surplus too low not doing anything')
                        print(json.dumps(envoy_data))
        else:
            print('car is not plugged in')
            print(teslafi_dict['charging_state'])
    else:
        print('Car is not home, not doing anything')
        print(teslafi_dict['location'])
