from setuptools import setup

setup(
   name='dsmr-mqtt-wrapper',
   version='0.01',
   description='Read Dutch Smart Meter data and publish it to using MQTT',
   author='Freek vH',
   author_email='freek@protonmail.ch',
   setup_requires=['wheel'],
   install_requires=['pyyaml', 'paho-mqtt', 'dsmr-parser'],
)
