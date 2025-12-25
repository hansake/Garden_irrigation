#!/usr/bin/python

"""
    water-valve.py

    Irregation water valve solenoid control.
    Switches the water valve solenoids on and off
    controlled by MQTT messages from Home Assistant.

"""

import RPi.GPIO as GPIO, time, os
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json

# Debug flag for printing, 0: false, 1: true,
# 2: print but do not publish, 3: print more verbose
Debug = 3

# Configuration for MQTT broker
broker_address = "192.168.42.59"
mqttUser = "mqtt_user"
mqttPassword = "use_mqtt"

# GPIO pin numbers
ctrlpin1 = 23 # Valve 1
ctrlpin2 = 24 # Valve 2
ctrlpin3 = 25 # Valve 3

# MQTT Connect / Disconnect
def on_connect(client, userdata, flags, rc, properties):
   print("Connected With Result Code ", rc)

def on_disconnect(client, userdata, rc):
   print("Client Got Disconnected With Result Code ", rc)

# MQTT subscribe handler
def on_message(client, userdata, message):
    if Debug > 0:
        print("Valve topic: "+message.topic)
        print("Valve message: "+message.payload.decode())
    match message.payload.decode():
        case "ON1":
            GPIO.output(ctrlpin1, GPIO.HIGH)
            # Publish state for valve switch 1
            state_topic_1 = "home/garden/garden_water_1_switch"
            state_data_1 = "ON1"
            if Debug > 0:
                print(state_topic_1, ":", state_data_1)
            if Debug != 2:
                rc = client.publish(state_topic_1, state_data_1)
            if Debug > 2:
                print(rc)
        case "ON2":
            GPIO.output(ctrlpin2, GPIO.HIGH)
            # Publish state for valve switch 2
            state_topic_2 = "home/garden/garden_water_2_switch"
            state_data_2 = "ON2"
            if Debug > 0:
                print(state_topic_2, ":", state_data_2)
            if Debug != 2:
                rc = client.publish(state_topic_2, state_data_2)
            if Debug > 2:
                print(rc)
        case "ON3":
            GPIO.output(ctrlpin3, GPIO.HIGH)
            # Publish state for valve switch 3
            state_topic_3 = "home/garden/garden_water_3_switch"
            state_data_3 = "ON3"
            if Debug > 0:
                print(state_topic_3, ":", state_data_3)
            if Debug != 2:
                rc = client.publish(state_topic_3, state_data_3)
            if Debug > 2:
                print(rc)
        case "OFF1":
            GPIO.output(ctrlpin1, GPIO.LOW)
            # Publish state for valve switch 1
            state_topic_1 = "home/garden/garden_water_1_switch"
            state_data_1 = "OFF1"
            if Debug > 0:
                print(state_topic_1, ":", state_data_1)
            if Debug != 2:
                rc = client.publish(state_topic_1, state_data_1)
            if Debug > 2:
                print(rc)
        case "OFF2":
            GPIO.output(ctrlpin2, GPIO.LOW)
            # Publish state for valve switch 2
            state_topic_2 = "home/garden/garden_water_2_switch"
            state_data_2 = "OFF2"
            if Debug > 0:
                print(state_topic_2, ":", state_data_2)
            if Debug != 2:
                rc = client.publish(state_topic_2, state_data_2)
            if Debug > 2:
                print(rc)
        case "OFF3":
            GPIO.output(ctrlpin3, GPIO.LOW)
            # Publish state for valve switch 3
            state_topic_3 = "home/garden/garden_water_3_switch"
            state_data_3 = "OFF3"
            if Debug > 0:
                print(state_topic_3, ":", state_data_3)
            if Debug != 2:
                rc = client.publish(state_topic_3, state_data_3)
            if Debug > 2:
                print(rc)

# Main routine creating  MQTT devices and listening for SQL commands
def main():

    # Setup handling of GPIO output pins to control
    # valve solenoids
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(ctrlpin1, GPIO.OUT)
    last_val_pin1 = GPIO.input(ctrlpin1)
    GPIO.setup(ctrlpin2, GPIO.OUT)
    last_val_pin2 = GPIO.input(ctrlpin2)
    GPIO.setup(ctrlpin3, GPIO.OUT)
    last_val_pin3 = GPIO.input(ctrlpin3)

    if Debug != 2:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Garden water valves")
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message
        client.username_pw_set(mqttUser, mqttPassword)
        client.connect(broker_address, 1883)
        client.subscribe("home/garden/garden_water_1_switch/set", qos = 1)
        client.subscribe("home/garden/garden_water_2_switch/set", qos = 1)
        client.subscribe("home/garden/garden_water_3_switch/set", qos = 1)

    client.loop_start()
    time.sleep(1)

    # Create MQTT water valve switches

    # Create water valve switch 1
    config_topic_1 = "homeassistant/switch/garden_water_1_switch/config"
    payload1 = {"unique_id": "garden_water_switch_1",
        "name": "Garden Water Switch 1",
        "state_topic": "home/garden/garden_water_1_switch",
        "command_topic": "home/garden/garden_water_1_switch/set",
        "availability_topic":"home/garden/garden_water_1_switch/available",
        "payload_on": "ON1",
        "payload_off": "OFF1",
        "state_on": "ON1",
        "state_off": "OFF1",
        "optimistic": False,
        "qos": 0,
        "retain": True
     }
    payload1 = json.dumps(payload1) #convert to JSON
    if Debug > 0:
        print(config_topic_1, ":", payload1)
    if Debug != 2:
        rc = client.publish(config_topic_1, payload1, qos = 0, retain = True)
    if Debug > 2:
        print(rc)
    time.sleep(1)
    # Send online message
    online_topic_1 = "home/garden/garden_water_1_switch/available"
    online_data_1 = "online"
    if Debug > 0:
        print(online_topic_1, ":", online_data_1)
    if Debug != 2:
        rc = client.publish(online_topic_1, online_data_1)
    if Debug > 2:
        print(rc)

    # Create water valve switch 2
    config_topic_2 = "homeassistant/switch/garden_water_2_switch/config"
    payload2 = {"unique_id": "garden_water_switch_2",
        "name": "Garden Water Switch 2",
        "state_topic": "home/garden/garden_water_2_switch",
        "command_topic": "home/garden/garden_water_2_switch/set",
        "availability_topic":"home/garden/garden_water_2_switch/available",
        "payload_on": "ON2",
        "payload_off": "OFF2",
        "state_on": "ON2",
        "state_off": "OFF2",
        "optimistic": False,
        "qos": 0,
        "retain": True
     }
    payload2 = json.dumps(payload2) #convert to JSON
    if Debug > 0:
        print(config_topic_2, ":", payload2)
    if Debug != 2:
        rc = client.publish(config_topic_2, payload2, qos = 0, retain = True)
    if Debug > 2:
        print(rc)
    time.sleep(1)
    # Send online message
    online_topic_2 = "home/garden/garden_water_2_switch/available"
    online_data_2 = "online"
    if Debug > 0:
        print(online_topic_2, ":", online_data_2)
    if Debug != 2:
        rc = client.publish(online_topic_2, online_data_2)
    if Debug > 2:
        print(rc)

    # Create water valve switch 3
    config_topic_3 = "homeassistant/switch/garden_water_3_switch/config"
    payload3 = {"unique_id": "garden_water_switch_3",
        "name": "Garden Water Switch 3",
        "state_topic": "home/garden/garden_water_3_switch",
        "command_topic": "home/garden/garden_water_3_switch/set",
        "availability_topic":"home/garden/garden_water_3_switch/available",
        "payload_on": "ON3",
        "payload_off": "OFF3",
        "state_on": "ON3",
        "state_off": "OFF3",
        "optimistic": False,
        "qos": 0,
        "retain": True
     }
    payload3 = json.dumps(payload3) #convert to JSON
    if Debug > 0:
        print(config_topic_3, ":", payload3)
    if Debug != 2:
        rc = client.publish(config_topic_3, payload3, qos = 0, retain = True)
    if Debug > 2:
        print(rc)
    time.sleep(1)
    # Send online message
    online_topic_3 = "home/garden/garden_water_3_switch/available"
    online_data_3 = "online"
    if Debug > 0:
        print(online_topic_3, ":", online_data_3)
    if Debug != 2:
        rc = client.publish(online_topic_3, online_data_3)
    if Debug > 2:
        print(rc)

    online_loop = 0
    publish_states = False
    while True:
        # Send online messages but not too often
        online_loop += 1
        if online_loop > 10:
            online_loop = 0
            online_topic_1 = "home/garden/garden_water_1_switch/available"
            online_data_1 = "online"
            if Debug > 0:
                print(online_topic_1, ":", online_data_1)
            if Debug != 2:
                rc = client.publish(online_topic_1, online_data_1)
            if Debug > 2:
                print(rc)
            time.sleep(1)
            online_topic_2 = "home/garden/garden_water_2_switch/available"
            online_data_2 = "online"
            if Debug > 0:
                print(online_topic_2, ":", online_data_2)
            if Debug != 2:
                rc = client.publish(online_topic_2, online_data_2)
            if Debug > 2:
                print(rc)
            time.sleep(1)
            online_topic_3 = "home/garden/garden_water_3_switch/available"
            online_data_3 = "online"
            if Debug > 0:
                print(online_topic_3, ":", online_data_3)
            if Debug != 2:
                rc = client.publish(online_topic_3, online_data_3)
            if Debug > 2:
                print(rc)
            time.sleep(1)

            publish_states = True

        # Listen for GPIO pin changing state for valve 1
        val_pin1 = GPIO.input(ctrlpin1)
        if (last_val_pin1 != val_pin1 or publish_states):
            last_val_pin1 = val_pin1
            # Publish state for valve switch 1
            state_topic_1 = "home/garden/garden_water_1_switch"
            if val_pin1:
                state_data_1 = "ON1"
            else:
                state_data_1 = "OFF1"
            if Debug > 0:
                print(state_topic_1, ":", state_data_1)
            if Debug != 2:
                rc = client.publish(state_topic_1, state_data_1)
            if Debug > 2:
                print(rc)

        # Listen for GPIO pin changing state for valve 2
        val_pin2 = GPIO.input(ctrlpin2)
        if (last_val_pin2 != val_pin2 or publish_states):
            last_val_pin2 = val_pin2
            # Publish state for valve switch 2
            state_topic_2 = "home/garden/garden_water_2_switch"
            if val_pin2:
                state_data_2 = "ON2"
            else:
                state_data_2 = "OFF2"
            if Debug > 0:
                print(state_topic_2, ":", state_data_2)
            if Debug != 2:
                rc = client.publish(state_topic_2, state_data_2)
            if Debug > 2:
                print(rc)

        # Listen for GPIO pin changing state for valve 3
        val_pin3 = GPIO.input(ctrlpin3)
        if (last_val_pin3 != val_pin3 or publish_states):
            last_val_pin3 = val_pin3
            # Publish state for valve switch 3
            state_topic_3 = "home/garden/garden_water_3_switch"
            if val_pin3:
                state_data_3 = "ON3"
            else:
                state_data_3 = "OFF3"
            if Debug > 0:
                print(state_topic_3, ":", state_data_3)
            if Debug != 2:
                rc = client.publish(state_topic_3, state_data_3)
            if Debug > 2:
                print(rc)

        publish_states = False

        # Wait a while before next update
        time.sleep(2)

if __name__ == '__main__':
    main()
