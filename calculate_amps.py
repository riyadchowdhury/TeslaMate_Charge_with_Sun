import db_functions


def calculate_required_amps(surplus, voltage):
    amps = surplus // voltage
    if amps < 32:
        return amps
    else:
        return 32


def calculate_increase_amps(surplus, current_car_amps, voltage):
    amps = surplus // voltage
    new_amps = amps + current_car_amps
    if new_amps < 32:
        return int(new_amps)
    else:
        return 32


def calculate_decrease_amps(surplus, current_car_amps, voltage):
    amps = abs(surplus) // voltage
    new_amps = current_car_amps - amps
    if new_amps < 0:
        return 0
    else:
        return int(new_amps)
