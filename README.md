# Garden and Greenhouse Irrigation

This garden and greenhouse irrigation system is using a Raspberry Pi 4 to control water valves and
to measure water flow through the valves.

The hardware schematics are created with KiCad version 9.0. The PCB layout created from the schematic
is not really exactly as the actual hardware design as the connections are not etched on a PCB board but soldered
with wires.

The control software is written in Python and creates devices with MQTT and these devices are controlled
from an MQTT interface in Home Assistant.

Photos of the hardware desingn will be added to this repository.
