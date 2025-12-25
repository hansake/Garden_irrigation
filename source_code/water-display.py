# water-display.py
# Show garden water irrigation status on OLED display
#
# Most of the code copied from the source below.
#
# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

import RPi.GPIO as GPIO, sqlite3 as sqlite

# Debug flag for printing, 0: false, 1: true,
# 2: print but do not publish, 3: print in detail
Debug = 0

# Put the display on for ~30 seconds
display_on = 30

# Setup haandling of the display switch
def switch_callback(pin):
    global display_on
    if Debug > 0:
        print("Display on switch pin: {0}".format(pin))
    display_on = 30

GPIO.setmode(GPIO.BCM)

switchpin = 18
GPIO.setup(switchpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(switchpin, GPIO.FALLING, callback=switch_callback)

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

while True:

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    if 0 < display_on:
        display_on -= 1
        # Get the liter water meter counters
        if Debug > 0:
            print("Get water counters")
        try:
            dbconn=sqlite.connect("/var/db/watermon.db")
            dbdata=dbconn.cursor()
            dbdata.execute("SELECT * FROM Wcounters ORDER BY ROWID DESC LIMIT 1")
        except sqlite.Error as e:
            print (e)
        row = dbdata.fetchone()
        if row is not None:
            watercounter1 = row[4]
            watercounter2 = row[5]
            watercounter3 = row[6]
        else:
            watercounter1 = 0
            watercounter2 = 0
            watercounter3 = 0
        if dbconn:
            dbconn.close()

        valve_state_1 = subprocess.check_output("gpio read 4", shell=True).decode("utf-8")
        if (valve_state_1.startswith("0")):
            on_off_1 = "OFF"
        else:
            on_off_1 = "ON "
        valve_text_1 = f"Valve 1: {on_off_1} {watercounter1} L "
        if Debug > 0:
            print(valve_text_1)

        valve_state_2 = subprocess.check_output("gpio read 5", shell=True).decode("utf-8")
        if (valve_state_2.startswith("0")):
            on_off_2 = "OFF"
        else:
            on_off_2 = "ON "
        valve_text_2 = f"Valve 2: {on_off_2} {watercounter2} L "
        if Debug > 0:
            print(valve_text_2)

        valve_state_3 = subprocess.check_output("gpio read 6", shell=True).decode("utf-8")
        if (valve_state_3.startswith("0")):
            on_off_3 = "OFF"
        else:
            on_off_3 = "ON "
        valve_text_3 = f"Valve 3: {on_off_3} {watercounter3} L "
        if Debug > 0:
            print(valve_text_3)

        # Write three lines of text.
        draw.text((x, top + 0), valve_text_1, font=font, fill=255)
        draw.text((x, top + 10), valve_text_2, font=font, fill=255)
        draw.text((x, top + 20), valve_text_3, font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.show()

    time.sleep(1)
