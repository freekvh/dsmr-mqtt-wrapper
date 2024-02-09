#!/usr/bin/env python3
# 
# connects to a serial or TCP port on a remote serial-to-TCP bridge.
#   the serial connection receives smart meter data every few seconds or so via a IR-head
#   topics of interest (OBIS parameters) are translated 1:1 to a (sub) topic 
#   each is separetly propagated via MQTT to a broker
# 
# tested to work with dsmr_parser 1.31 and the same setup as for https://github.com/ndokter/dsmr_parser/pull/92
#
# TODO: restructure to HA MQTT Discovery per https://www.home-assistant.io/integrations/mqtt/
#   use Q3D_EQUIPMENT_IDENTIFIER as object_id
#   <discovery_prefix>/<component>/[<node_id>/]<object_id>/config
# TODO: send birth/retain/QOS2 ?
# TODO: test parallel subscription by evcc

# International generalized additions
# ELECTRICITY_IMPORTED_TOTAL    = :1.8.0    # Total imported energy register (P+)
# ELECTRICITY_EXPORTED_TOTAL    = :2.8.0    # Total exported energy register (P-)
# CURRENT_ELECTRICITY_USAGE     = :1.7.0
# CURRENT_ELECTRICITY_DELIVERY  = :2.7.0
# Q3D_EQUIPMENT_IDENTIFIER      = :0.0.0    # Logical device name
# Q3D_EQUIPMENT_SERIALNUMBER    = :96.1.255 # Device Serialnumber

from functools import partial
import asyncio
import yaml
import paho.mqtt.client as mqtt
from dsmr_parser.clients import create_dsmr_reader, create_tcp_dsmr_reader
import argparse

DEBUG = False
config_file = 'config.yaml'

def mqtt_topic_callback(mqtt_client, topic, telegram):
    if DEBUG:
        print(telegram)
    for k,v in telegram:
        if k in config['values_of_interest']:
            published = mqtt_client.publish(topic + '/' + k, payload=float(v.value), qos=0)
            if DEBUG:
                print("published: ", topic + '/' + k,v.value,v.unit, " > ", published)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DSMR to MQTT bridge')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-c', '--config', help='Load config from (default '+config_file+')')
    args = parser.parse_args()
    DEBUG = args.verbose
    if args.config:
        config_file = args.config

    with open(config_file) as file:
        config = yaml.safe_load(file)#, Loader=yaml.FullLoader)
        if config:
            if DEBUG:
                print(config)
            mqtt_client = mqtt.Client(config['mqtt_client_name'])
            if 'mqtt_username' in config:
                mqtt_client.username_pw_set(config['mqtt_username'], password=config['mqtt_password'])
            mqtt_client.reconnect_delay_set(min_delay=1, max_delay=120)
            mqtt_client.connect(config['mqtt_broker_address'])

            mqtt_callback = partial(mqtt_topic_callback, mqtt_client, config['topic'])

            loop = asyncio.get_event_loop()

            if 'client' in config:
                if config['client'] == 'tcp':
                    create_connection = partial(create_tcp_dsmr_reader,
                                        config['host'], config['port'], config['telegram_specification'],
                                        mqtt_callback, loop=loop)                    
                    try:
                        while True:
                            conn = create_connection()
                            transport, protocol = loop.run_until_complete(conn)
                            loop.run_until_complete(protocol.wait_closed())
                            loop.run_until_complete(asyncio.sleep(5))
                    except KeyboardInterrupt:
                        if 'transport' in locals():
                            transport.close()
                        loop.run_until_complete(asyncio.sleep(0))
                    finally:
                        loop.close()
                elif config['client'] == 'serial':
                    # Set the parameters for dsmr_parser
                    serial_reader = SerialReader(
                        device='/dev/ttyUSB0',
                        serial_settings=SERIAL_SETTINGS_V5,
                        telegram_specification=telegram_specifications.V4
                    )
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
