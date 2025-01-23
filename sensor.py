# Sensor.py
from DBconnector import dbLog
import datetime
from functools import partial

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

RLED = 17
YLED = 4
GLED = 6

GPIO.setup(RLED, GPIO.OUT)
GPIO.setup(YLED, GPIO.OUT)
GPIO.setup(GLED, GPIO.OUT)

# Definierte GPIO-Pins
PIR_GPIO = 21  # Bewegungsmelder-Eingang
#PIR_GPIO2 = 19  # LED-Ausgang oder anderes Ausgangsgerät

# GPIO-Setup und Initialisierung
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(PIR_GPIO2, GPIO.OUT)
GPIO.setwarnings(False)

# Callback-Funktion für Bewegungserkennung
def motion_detected_callback(channel, con):
    print("Motion detected at " + str(time.ctime()))
    #GPIO.output(PIR_GPIO2, GPIO.HIGH)

    #Datenprotokollierung: 
    Date = datetime.datetime.now()
    Event = "Bewegung festgestellt"
    User = None

    GPIO.output(YLED, GPIO.HIGH)

    dbLog(con, Date, Event, User)

    time.sleep(2)
    GPIO.output(YLED, GPIO.LOW)
    #GPIO.output(PIR_GPIO2, GPIO.LOW)

# Event-Handler-Funktion zum Starten des Bewegungssensors
def setup_motion_sensor(conn):
    con = conn
    callback_with_con = partial(motion_detected_callback, con=con)
    GPIO.add_event_detect(PIR_GPIO, GPIO.RISING, callback=callback_with_con)
    print("Bewegungssensor aktiv.")

# Clean-up Funktion
def cleanup():
    GPIO.cleanup()
