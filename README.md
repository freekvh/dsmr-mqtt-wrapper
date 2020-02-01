# dsmr-mqtt-wrapper
This program is intended to run on a Raspberry Pi attached to a Dutch smart
electricity/gas meter with a P1 cable. It receives the data and publishes the
selected information to an MQTT topic. It is configured via a single YAML file
and leans heavily on the dsmr_parser library from Nigel Dokter (Github).

## Instalation
Optionally create a virtual environment and enter it, on Raspbian do;

`sudo apt-get install python3-venv`

`python3 -m venv ~/.venv/dsmr-mqtt-wrapper`

`source ~/.venv/dsmr-mqtt-wrapper/bin/activate`

`pip3 install wheel`


Clone this git repository

`git clone https://gitlab.com/freekvh/dsmr-mqtt-wrapper.git`

Add a line in the crontab so that the script starts at boot, if you cloned this
repo to ~/projects (/home/pi/projects), add the following line:

`@reboot /bin/bash -c 'cd $HOME/dsmr-mqtt-wrapper && source $HOME/.venv/dsmr-mqtt-wrapper/bin/activate && ./dsmr-mqtt-wrapper.py' > /dev/null 2>&1`