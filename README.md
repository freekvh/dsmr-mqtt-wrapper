# dsmr-mqtt-wrapper

This program reads the information from a Dutch Smart Electricity/Gas usage meter and publishes the results to an MQTT topic. It is configured via a single YAML file and leans heavily on the dsmr_parser library from Nigel Dokter (Github).

## Instalation
Optionally create a virtual environment and enter it, on Raspbian do;

`sudo apt-get install python3-venv`
`python3 -m venv ~/.venv/dsmr-mqtt-wrapper`
`source ~/.venv/dsmr-mqtt-wrapper/bin/activate`
`pip3 install wheel`

