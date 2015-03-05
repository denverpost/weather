#!/usr/bin/env python
from setuptools import setup, Command
import subprocess


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call(['python -m py.test'])
        raise SystemExit(errno)

setup(
    name='Weather',
    version='0.1',
    description='A publishing tool for weather data',
    license='Apache',
    url='https://github.com/denverpost/weather',
    author='Joe Murphy',
    author_email='joe.murphy@gmail.com',
    packages=['weather'],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    )

