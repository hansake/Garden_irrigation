# Garden irrigation control software

The software controls the interface board described in the schematics folder
and also the OLED display.

This software is installed on Raspberry Pi 4 with
Raspberry Pi OS 64 bit and a Micro SD 64GB storage device.

The control software is written in Python and creates and is controlled
from an MQTT interface in Home Assistant.

There is also a web interface that may be used to control the interface board.

## Prerequsites for Garden irrigation control software

A web server handling PHP (I am using Nginx)
* [How to Install PHP on a Raspberry Pi - FlatCoding](https://flatcoding.com/tutorials/php/how-to-install-php-on-a-raspberry-pi/)

WiringPi
* [WiringPi/WiringPi: The arguably fastest GPIO Library for the Raspberry Pi](https://github.com/WiringPi/WiringPi)

## Installation of software and control scripts

Copy these Python files to /usr/local/bin
* water-display.py
* water-meter.py
* water-valve.py

Copy these control scripts to /etc/init.d
* water-display.service
* water-meter.service
* water-valve.service

Copy this PHP file to /var/www/html
* garden.php

Start the Python scripts as services
```
$ sudo systemctl start water-meter
$ sudo systemctl enable water-meter
$ sudo systemctl start water-valve
$ sudo systemctl enable water-valve
$ sudo systemctl start water-display
$ sudo systemctl enable water-display
```
