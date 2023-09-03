import db_functions
import teslamate_api
import calculate_amps
import json
import logging

logger = logging.getLogger(__name__)


def mainfunction(envoy_data=None):
    config = db_functions.get_config_from_db()
    logging.info('Charge mode is set to: %s', config['charge_mode'])
    # If charge mode is set to grid don't do anything
    if config['charge_mode'] == 'grid':
        logging.info(
            f"Charge mode is set to {config['charge_mode']} so not doing anything")
        return
    teslamate = teslamate_api.TeslaMate()
    if teslamate.is_car_home():
        if teslamate.is_car_plugged_in():
            battery_level = teslamate.get_battery_level()
            voltage = teslamate.get_voltage(int(config['voltage']))
            max_soc = teslamate.get_max_soc()
            # low battery charge no matter what
            if battery_level < int(config['minimum_battery_level']):
                max_amps = teslamate.get_max_amps()
                teslamate.set_charging_amps(max_amps)
                teslamate.start_charge()
            # high battery stop charging
            elif battery_level >= max_soc:
                teslamate.stop_charge()
            else:
                # car already charging
                if teslamate.is_car_charging():
                    current_amps = teslamate.get_current_amps()
                    if current_amps is None:
                        logging.warning(
                            'Couldnt get current amps not doing anything')
                        return
                    current_car_consumption = current_amps * voltage
                    if envoy_data is None:
                        envoy_data = db_functions.read_envoy_data_from_db()
                    rest_house_consuption = envoy_data['consumption'] - \
                        current_car_consumption
                    if (rest_house_consuption) > envoy_data['production']:
                        logging.info(
                            'House is using too much power, stopping charge')
                        teslamate.stop_charge()
                    elif envoy_data['surplus'] > 250:
                        logging.info(
                            'Still surplus left increase amps')
                        logging.debug('Current envoy data: %s', envoy_data)
                        new_amps = calculate_amps.calculate_increase_amps(
                            envoy_data['surplus'], current_amps, voltage)
                        logging.info('Increasing amps to: %s', new_amps)
                        teslamate.set_charging_amps(new_amps)
                        teslamate.start_charge()
                    elif envoy_data['surplus'] <= 0:
                        logging.info(
                            'Negetive surplus lets lower amps')
                        logging.debug('Current envoy data: %s', envoy_data)
                        new_amps = calculate_amps.calculate_decrease_amps(
                            envoy_data['surplus'], current_amps, voltage)
                        logging.info('Lowering amps to: %s', new_amps)
                        teslamate.set_charging_amps(new_amps)
                        teslamate.start_charge()
                    else:
                        logging.info(
                            'Everything is balanced not doing anything')
                else:  # car not charging
                    if envoy_data is None:
                        envoy_data = db_functions.read_envoy_data_from_db()
                    if envoy_data['surplus'] > int(config['minimum_watt']):
                        required_amps = calculate_amps.calculate_required_amps(
                            envoy_data['surplus'], voltage)
                        logging.info(
                            'Starting charge, setting current to : %s', new_amps)
                        teslamate.set_charging_amps(required_amps)
                        teslamate.start_charge()
                    else:
                        logging.info(
                            'Surplus too low not doing anything')
                        logging.debug('Current envoy data: %s', envoy_data)
        else:
            logging.info(
                'Car is not plugged in')
    else:
        logging.info(
            'Car is not home')
