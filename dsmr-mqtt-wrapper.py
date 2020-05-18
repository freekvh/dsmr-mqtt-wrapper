#!/usr/bin/env python3
# Based on example code: DSMR v4.2 p1 using dsmr_parser and telegram objects

# Todo
# - Debugging mode where everything is printed optionally

from dsmr_parser import telegram_specifications
from dsmr_parser.clients import SerialReader, SERIAL_SETTINGS_V5
from dsmr_parser.objects import CosemObject, MBusObject, Telegram
from dsmr_parser.parsers import TelegramParser
import os
import yaml
import paho.mqtt.client as mqtt


# Load the config file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Set the parameters for dsmr_parser
serial_reader = SerialReader(
    device='/dev/ttyUSB0',
    serial_settings=SERIAL_SETTINGS_V5,
    telegram_specification=telegram_specifications.V4
)

# Initiate the mqtt connection
client = mqtt.Client(config['mqtt_client_name'])
if 'mqtt_username' in config:
    client.username_pw_set(config['mqtt_username'], password=config['mqtt_password'])
client.reconnect_delay_set(min_delay=1, max_delay=120)
client.connect(config['mqtt_broker_address'])

# Get all the telegram's values into a dictionary
for telegram in serial_reader.read_as_object():
    telegram_dict = {attr: [value.value, value.unit] for attr, value in telegram}
    # If the telegram does not contain ELECTRICITY_USED_TARIFF_ALL, calculate it here
    if not 'ELECTRICITY_USED_TARIFF_ALL' in config:
        telegram_dict['ELECTRICITY_USED_TARIFF_ALL'] = [
                (telegram_dict['ELECTRICITY_USED_TARIFF_1'][0] + 
                telegram_dict['ELECTRICITY_USED_TARIFF_2'][0]),
                telegram_dict['ELECTRICITY_USED_TARIFF_1'][1]
                ]
    for value in config['values_of_interest']:
        client.publish(config['topic'] + '/' + value, float(telegram_dict[value][0]))

