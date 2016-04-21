#! /usr/bin/python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Bachelorthesis - Prototypical Development of a System for the Analysis of Driving Behaviour for Motor Vehicles',
    'author': 'Daniel Grewe',
    'url': 'https://github.com/dgrew07/ba-iot-prototype',
    'download_url': 'https://github.com/dgrew07/ba-iot-prototype',
    'author_email': 'd_grew07@uni-muenster.de',
    'version': '0.1',
    # require 'nose' for testing
    'install_requires': [],
    'packages': ['beaconpy'],
    'scripts': [],
    'name': 'beacon'
}

setup(**config)