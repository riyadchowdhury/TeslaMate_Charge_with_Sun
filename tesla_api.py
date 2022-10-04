import json
import time
import requests

def set_charging_amps(token, amps, teslafi_dict):
    if amps < 5: #tesla api does not allow charging less than 5 amps
        amps = 5
    if int(teslafi_dict['charge_current_request']) != amps:
        r = requests.get(
            f"https://www.teslafi.com/feed.php?command=set_charging_amps&charging_amps={amps}&wake=20",
            headers={
                'Authorization': f"Bearer {token}"
            }
        )
        if r.status_code != 200:
            print("Error setting charge")
        else:
            print(f"car set to {amps} amps")
    else:
        print(f"car already set to charge at {amps} amps")

def get_tesla_feed(token):
    r = requests.get(
        f"https://www.teslafi.com/feed.php",
        headers={
            'Authorization': f"Bearer {token}"
        }
    )
    feed = r.json()
    if feed['charging_state'] is None:
        r_lastgood = requests.get(
            f"https://www.teslafi.com/feed.php?command=lastGood",
            headers={
                'Authorization': f"Bearer {token}"
            }
        )
        return r_lastgood.json()
    else:
        return feed

def is_car_plugged_in(token, teslafi_dict):
    if teslafi_dict['charging_state'] == 'Disconnected':
        return False
    else:
        return True

def is_car_home(teslafi_dict):
    if teslafi_dict['location'] == 'Home':
        return True
    else:
        return False

def is_car_charging(teslafi_dict):
    if teslafi_dict['charging_state'] == 'Charging':
        return True
    else:
        return False

def get_battery_level(teslafi_dict):
    return int(teslafi_dict['battery_level'])

def get_current_amps(teslafi_dict):
    current_amps = int(teslafi_dict['charge_current_request'])
    if teslafi_dict['charge_current_request'] is None:
        current_amps = 32
    if current_amps < 5:
        current_amps = 5
    return current_amps

def start_charge(token, teslafi_dict):
    if teslafi_dict['charging_state'] != 'Charging':
        r = requests.get(
            f"https://www.teslafi.com/feed.php?command=charge_start&wake=20",
            headers={
                'Authorization': f"Bearer {token}"
            }
        )
        if r.status_code != 200:
            print("Error setting charge")
        else:
            print("starting charge")
    else:
        print('car already charging')

def stop_charge(token, teslafi_dict):
    if teslafi_dict['charging_state'] == 'Charging':
        r = requests.get(
            f"https://www.teslafi.com/feed.php?command=charge_stop&wake=20",
            headers={
                'Authorization': f"Bearer {token}"
            }
        )
        if r.status_code != 200:
            print("Error setting charge")
        else:
            print("stopping charge")
    else:
        print('car not charging nothing to stop, current state ' + teslafi_dict['charging_state'])

def calculate_required_amps(surplus):
    amps = surplus // 238;
    if amps < 32:
        return amps
    else:
        return 32

def calculate_increase_amps(surplus, current_car_amps):
    amps = surplus // 238;
    new_amps = amps + current_car_amps
    if new_amps < 32:
        return int(new_amps)
    else:
        return 32

def calculate_decrease_amps(surplus, current_car_amps):
    amps = abs(surplus) // 238;
    new_amps = current_car_amps - amps
    if new_amps < 0:
        return 0
    else:
        return int(new_amps)
