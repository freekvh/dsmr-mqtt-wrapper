# dsmr-mqtt-wrapper
This program is intended to run on a Raspberry Pi attached to a Dutch smart
electricity/gas meter with a P1 cable. It receives the data and publishes the
selected information to an MQTT topic. It is configured via a single YAML file
and leans heavily on the dsmr_parser library from Nigel Dokter (Github).

## Installation
Optionally create a virtual environment and enter it, on Raspbian do;

`sudo apt-get install python3-venv`

`python3 -m venv ~/.venv/dsmr-mqtt-wrapper`

`source ~/.venv/dsmr-mqtt-wrapper/bin/activate`

`pip3 install wheel`


Clone this git repository

`git clone https://gitlab.com/freekvh/dsmr-mqtt-wrapper.git`

## Configuration
In the config.yaml file, change the value for mqtt_broker_address to the address
of your mqtt broker.

Add a line in the crontab so that the script starts at boot, if you cloned this
repo to the home directory of the pi user (/home/pi), add the following line:

`@reboot /bin/bash -c 'cd $HOME/dsmr-mqtt-wrapper && source $HOME/.venv/dsmr-mqtt-wrapper/bin/activate && ./dsmr-mqtt-wrapper.py' > /dev/null 2>&1`

## Configuring Home Assistant
By adding the following lines to your Home Assistant configuration.yaml the
smart meter values can be read:

```yaml
mqtt:
  broker: mqtt_broker_address

sensor:
  - platform: mqtt
    name: "Current usage"
    state_topic: "home/smart_meter/CURRENT_ELECTRICITY_USAGE"
    unit_of_measurement: 'kW'

  - platform: mqtt
    name: "Electricity used"
    state_topic: "home/smart_meter/ELECTRICITY_USED_TARIFF_ALL"
    unit_of_measurement: 'kWh'

  - platform: mqtt
    name: "Gas consumed"
    state_topic: "home/smart_meter/HOURLY_GAS_METER_READING"
    unit_of_measurement: 'm3'
```
