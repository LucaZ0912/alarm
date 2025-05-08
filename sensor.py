# Sensor.py
from DBconnector import dbLog
import datetime
from functools import partial

from picamera import PiCamera
from time import sleep
import os

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
PIR_GPIO2 = 5 #PommesSchranke 

# GPIO-Setup und Initialisierung
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIR_GPIO2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(PIR_GPIO2, GPIO.OUT)
GPIO.setwarnings(False)

# Callback-Funktion für Bewegungserkennung
def motion_detected_callback(channel, con):
    print("Motion detected at " + str(time.ctime()))
    Picpath = capture_image()

    #Datenprotokollierung: 
    Date = datetime.datetime.now()
    Event = "Bewegung festgestellt"
    User = None

    GPIO.output(YLED, GPIO.HIGH)

    dbLog(con, Date, Event, User, Picpath)

    time.sleep(2)
    GPIO.output(YLED, GPIO.LOW)
    #GPIO.output(PIR_GPIO2, GPIO.LOW)

# Callback-Funktion für PommesSchranke
def pommes_detected_callback(channel, con):
    print("Pommes Schranke aktiviert at " + str(time.ctime()))

    #Datenprotokollierung: 
    Date = datetime.datetime.now()
    Event = "Lichtschranke aktiviert"
    User = None

    # Gelbe LED blinkt zweimal
    for _ in range(2):
        GPIO.output(YLED, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(YLED, GPIO.LOW)
        time.sleep(0.5)

    dbLog(con, Date, Event, User)

    GPIO.output(RLED, GPIO.LOW)

# Event-Handler-Funktion zum Starten beider Sensoren
def setup_motion_sensor(con):
    # Vollständiges GPIO Cleanup und Neuinitialisierung
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # LED Setup
    GPIO.setup(RLED, GPIO.OUT)
    GPIO.setup(YLED, GPIO.OUT)
    GPIO.setup(GLED, GPIO.OUT)
    
    # Sensor Setup
    GPIO.setup(PIR_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PIR_GPIO2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # Event-Detector für beide Sensoren hinzufügen
    motion_callback_with_con = lambda channel: motion_detected_callback(channel, con)
    pommes_callback_with_con = lambda channel: pommes_detected_callback(channel, con)
    
    GPIO.add_event_detect(PIR_GPIO, GPIO.RISING, callback=motion_callback_with_con)
    GPIO.add_event_detect(PIR_GPIO2, GPIO.RISING, callback=pommes_callback_with_con)
    
    print("Bewegungssensor und Pommes Schranke aktiv.")

def capture_image(save_dir="/home/it/it/captures"):
    # Sicherstellen, dass das Zielverzeichnis existiert
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Kamera initialisieren
    camera = PiCamera()
    camera.resolution = (1024, 768)

    # Kamera warmlaufen lassen
    camera.start_preview()
    sleep(2)

    # Bild aufnehmen
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(save_dir, f"image_{timestamp}.jpg")
    camera.capture(filename)
    camera.stop_preview()
    camera.close()

    print(f"Bild gespeichert: {filename}")
    return filename

# Clean-up Funktion
def cleanup():
    GPIO.cleanup()
