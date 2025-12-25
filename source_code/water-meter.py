#!/usr/bin/python

"""
    water-meter.py

    Irregation water meter.
    Measures water consumption using flow meters and
    stores the values in a SQLite database,
    based on the number of pulses from a flow meter.

    Handles three flow meter pulse inputs.
    The values are then published via MQTT to Home Assistant.

"""

import RPi.GPIO as GPIO, sqlite3 as sqlite, time, os
import paho.mqtt.client as mqtt

# Debug flag for printing, 0: false, 1: true,
# 2: print but do not publish, 3: print in detail
# 4: print for each pulse on a pin
Debug = 3

# Configuration for MQTT broker
broker_address = "192.168.42.59"
mqttUser = "mqtt_user"
mqttPassword = "use_mqtt"

# MQTT topics and states --- change to water
discoveryTopic1 = "homeassistant/sensor/garden_water_1/config"
stateTopic1 = "home/water_1/state"
discoveryTopic2 = "homeassistant/sensor/garden_water_2/config"
stateTopic2 = "home/water_2/state"
discoveryTopic3 = "homeassistant/sensor/garden_water_3/config"
stateTopic3 = "home/water_3/state"

# The flow meter pulse counters
# there will be <pulses_per_liter> pulses for each liter of water
pulsecounter1 = 0
pulsecounter2 = 0
pulsecounter3 = 0

# Pulses per liter should be calibrated
pulses_per_liter = 450

# MQTT Connect / Disconnect
def on_connect(client, userdata, flags, rc, properties):
   print("Connected With Result Code ", rc)

def on_disconnect(client, userdata, rc):
   print("Client Got Disconnected With Result Code ", rc)

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    if Debug > 0:
        print("create_connection")
    try:
        conn = sqlite.connect(db_file)
        return conn
    except sqlite.Error as e:
        print(e)

    return None

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    if Debug > 0:
        print("create_table")
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite.Error as e:
        print(e)

def InsertCounters(db_file, timestamp, cntr1, cntr2, cntr3, lcntr1, lcntr2, lcntr3):
    if Debug > 0:
        print("InsertCounters")
    try:
        dbconn=sqlite.connect(db_file)
        dbdata=dbconn.cursor()
        dbdata.execute("INSERT INTO Wcounters VALUES(?, ?, ?, ?, ?, ?, ?)", (timestamp, cntr1, cntr2, cntr3, lcntr1, lcntr2, lcntr3))
        dbconn.commit()
    except sqlite.Error as e:
        print (e)
        if dbconn:
            dbconn.rollback()
    finally:
        if dbconn:
            dbconn.close()

def GetCurrCounters(db_file):
    global pulsecounter1
    global pulsecounter2
    global pulsecounter3

    if Debug > 0:
        print("GetCurrCounters")
    try:
        dbconn=sqlite.connect(db_file)
        dbdata=dbconn.cursor()
        dbdata.execute("SELECT * FROM Wcounters ORDER BY ROWID DESC LIMIT 1")
    except sqlite.Error as e:
        print (e)
    row = dbdata.fetchone()
    if row is not None:
        pulsecounter1 = row[1]
        pulsecounter2 = row[2]
        pulsecounter3 = row[3]
    if dbconn:
        dbconn.close()

# GPIO input callback routines updating
# the water meter counters

def pulse1_callback(pin):
    global pulsecounter1
    if Debug > 3:
        print("pulse on pin: {0}".format(pin))
    pulsecounter1 += 1

def pulse2_callback(pin):
    global pulsecounter2
    if Debug > 3:
        print("pulse on pin: {0}".format(pin))
    pulsecounter2 += 1

def pulse3_callback(pin):
    global pulsecounter3
    if Debug > 3:
        print("pulse on pin: {0}".format(pin))
    pulsecounter3 += 1

# Main routine creating SQL database and MQTT devices
# then collecting water meter values and saving them in
# the SQL database and sending them to the MQTT brooker
def main():
    global pulsecounter1
    global pulsecounter2
    global pulsecounter3

    # Last pules counters
    lpc1 = 0
    lpc2 = 0
    lpc3 = 0

    # Setup handling of pulse input from water meters
    GPIO.setmode(GPIO.BCM)

    pulsepin1 = 13
    GPIO.setup(pulsepin1, GPIO.IN)

    pulsepin2 = 19
    GPIO.setup(pulsepin2, GPIO.IN)

    pulsepin3 = 26
    GPIO.setup(pulsepin3, GPIO.IN)

    GPIO.add_event_detect(pulsepin1, GPIO.RISING, callback=pulse1_callback, bouncetime=2)
    GPIO.add_event_detect(pulsepin2, GPIO.RISING, callback=pulse2_callback, bouncetime=2)
    GPIO.add_event_detect(pulsepin3, GPIO.RISING, callback=pulse3_callback, bouncetime=2)

    # Setup the SQL database
    database = "/var/db/watermon.db"

    sql_create_wcounters_table = """CREATE TABLE IF NOT EXISTS Wcounters (
                                    timestamp INTEGER PRIMARY KEY,
                                    wcounter1 INTEGER,
                                    wcounter2 INTEGER,
                                    wcounter3 INTEGER,
                                    wlcounter1 INTEGER,
                                    wlcounter2 INTEGER,
                                    wlcounter3 INTEGER
                                );"""

    # Create a database connection
    conn = create_connection(database)
    if conn is not None:
        # create water counters table
        create_table(conn, sql_create_wcounters_table)
    else:
        print("Error! cannot create the database connection.")

    timenow = int(time.time())

    # Get latest counter values
    GetCurrCounters(database)

    if Debug != 2:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Garden water meters")
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.username_pw_set(mqttUser, mqttPassword)
        client.connect(broker_address, 1883)

    client.loop_start()
    time.sleep(1)

    # Create MQTT sensors

    # Create water meter sensor 1
    mqttbuffer = "{\"name\":\"Garden water 1\",\
      \"stat_t\":\"%s\",\
      \"unique_id\":\"garden_water_1\",\
      \"unit_of_meas\":\"L\",\
      \"dev_cla\":\"water\",\
      \"frc_upd\":true,\
      \"val_tpl\":\"{{ value_json.water|default(0) }}\"}"\
      % stateTopic1
    if Debug > 0:
        print(discoveryTopic1, ":", mqttbuffer)
    if Debug != 2:
        rc = client.publish(discoveryTopic1, mqttbuffer, qos = 0, retain = True)
    if Debug > 2:
        print (rc)
    time.sleep(1)

    # Create water meter sensor 2
    mqttbuffer = "{\"name\":\"Garden water 2\",\
      \"stat_t\":\"%s\",\
      \"unique_id\":\"garden_water_2\",\
      \"unit_of_meas\":\"L\",\
      \"dev_cla\":\"water\",\
      \"frc_upd\":true,\
      \"val_tpl\":\"{{ value_json.water|default(0) }}\"}"\
      % stateTopic2
    if Debug > 0: 
        print(discoveryTopic2, ":", mqttbuffer)
    if Debug != 2: 
        rc = client.publish(discoveryTopic2, mqttbuffer, qos = 0, retain = True)
    if Debug > 2:
        print (rc)
    time.sleep(1)

    # Create water meter sensor 3
    mqttbuffer = "{\"name\":\"Garden water 3\",\
      \"stat_t\":\"%s\",\
      \"unique_id\":\"garden_water_3\",\
      \"unit_of_meas\":\"L\",\
      \"dev_cla\":\"water\",\
      \"frc_upd\":true,\
      \"val_tpl\":\"{{ value_json.water|default(0) }}\"}"\
      % stateTopic3
    if Debug > 0:
        print(discoveryTopic3, ":", mqttbuffer)
    if Debug != 2:
        rc = client.publish(discoveryTopic3, mqttbuffer, qos = 0, retain = True)
    if Debug > 2:
        print (rc)
    time.sleep(1)

    while True:
        if Debug > 0:
            print("Water: 1: {0} pulses, 2: {1} pulses, 3: {2} pulses".format(pulsecounter1, pulsecounter2, pulsecounter3))

        # Calculate liter counters to publish with MQTT
        wliter1 = int(pulsecounter1/pulses_per_liter)
        wliter2 = int(pulsecounter2/pulses_per_liter)
        wliter3 = int(pulsecounter3/pulses_per_liter)
        if Debug > 0:
            print("Water: 1: {0} L, 2: {1} L, 3: {2} L".format(wliter1, wliter2, wliter3))

        # Update SQLite database with counter values if changed
        if pulsecounter1 > lpc1 or pulsecounter2 > lpc2 or pulsecounter3 > lpc3:
            timenow = int(time.time())
            InsertCounters(database, timenow, pulsecounter1, pulsecounter2, pulsecounter3, wliter1, wliter2, wliter3)
            lpc1 = pulsecounter1
            lpc2 = pulsecounter2
            lpc3 = pulsecounter3

        # Format and publish water meter counter 1
        mqttbuffer = "{ \"water\" : \"%d\" }" % wliter1
        if Debug > 0:
            print(stateTopic1, ":", mqttbuffer)
        if Debug != 2:
            rc = client.publish(stateTopic1, mqttbuffer)
        if Debug > 2:
            print (rc)
        time.sleep(1)

        # Format and publish water meter counter 2
        mqttbuffer = "{ \"water\" : \"%d\" }" % wliter2
        if Debug > 0: 
            print(stateTopic2, ":", mqttbuffer)
        if Debug != 2: 
            rc = client.publish(stateTopic2, mqttbuffer)
        if Debug > 2:
            print (rc)
        time.sleep(1)

        # Format and publish water meter counter 3
        mqttbuffer = "{ \"water\" : \"%d\" }" % wliter3
        if Debug > 0: 
            print(stateTopic3, ":", mqttbuffer)
        if Debug != 2: 
            rc = client.publish(stateTopic3, mqttbuffer)
        if Debug > 2:
            print (rc)
        time.sleep(1)

        # Wait a while before next update
        time.sleep(10)

if __name__ == '__main__':
    main()
