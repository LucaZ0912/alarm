#============================================
#DoorSecruityThingy==========================
#Autor: Patrick Schweig, Luca Zickenheiner===
#GitHub: https://github.com/LucaZ0912/alarm==
#============================================


#==========ToDo's==========
#1. WebService: 
#           1.1 Ein WebServiceTool erstellen, auf der die Tabelle "Incidents" sowie der Status der Anlage ablesbar ist
#           1.2 Die Möglichkeit zur Anmeldung als Administrator mit ID und einem selbstgewählten Passwort
#           1.3 Ein Dashboard, auf dem die letzten Incidents direkt einsehbar sind und Änderungen an Einstellungen 
#               vorgenommen werden können.
#           1.4 Profit
#           1.5 den Scheiß verschlüsseln
# 
# 2. Dokumentation:
#                 2.1 Dokumentation machen :'( 


#==========Imports==========
#Standartimports
import time
import datetime
import os

#Bauteil-Bibliotheken
import RPi.GPIO as GPIO
import mfrc522
from mfrc522 import SimpleMFRC522
from mfrc522 import MFRC522


#imports aus eigenen beiliegenden Bibliotheken
import sensor
from DBconnector import get_db_connection, is_authorized, is_admin, dbLog, show_incidents

#==========Set Up==========
reader = SimpleMFRC522()
reader2 = MFRC522()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Einstellungen
#     Idee für Später: Einstellungen können im Dashboard verändert werden und werden dann beim
#                      Setup in die entsprechenden Variablen geladen. Einstellungsänderungen 
#                      werden auch in der Incidents Tabelle eingetragen und dokumentiert
sensorSetup = True
AdminSetup = False
didSetup = False #Wenn der Setup schon durchgeführt wurde, wird diese Variable auf True gesetzt

#==========Einstellungen==========
BUZZER_ENABLED = False  # Schalter für den Buzzer
BUZZER_PIN = 18

#Datenbankenverbindung herstellen
conn, connected = get_db_connection()

#=========="Beleuchtung"==========
RLED = 17
YLED = 4
GLED = 6

GPIO.setup(RLED, GPIO.OUT)
GPIO.setup(YLED, GPIO.OUT)
GPIO.setup(GLED, GPIO.OUT)


#==========FUNKTIONEN==========

def writeTag(reader): #Funktion zum Überschreiben den "Texts" auf dem Tag
    text = input('Enter tag data:')
    print("Hold tag to module")
    reader.write(text)
    print("Done...")
            
def readTag(reader): #Funktion zum lesen der "ID" und des "Texts" auf dem Tag
    id, text = reader.read()
    print(id)
    print(text)

def readAdmin(reader): #Funktion zum erkennen des Admin Status. 
    id, text = reader.read()
    isAdmin, name = is_admin(conn, id) #Gibt TRUE und den Namen zurück wenn die gegebene ID in der Datenbank mit dem Zusatz "Admin" hinterlegt ist
    if isAdmin:
        return True, name
    else: 
        return False, name

def setup_buzzer():
    if BUZZER_ENABLED:
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        global buzzer_pwm
        buzzer_pwm = GPIO.PWM(BUZZER_PIN, 440)
        buzzer_pwm.start(0)

def play_tone(frequency, duration=0.1):
    if not BUZZER_ENABLED:
        return
    buzzer_pwm.ChangeFrequency(frequency)
    buzzer_pwm.ChangeDutyCycle(50)
    time.sleep(duration)
    buzzer_pwm.ChangeDutyCycle(0)
    time.sleep(0.05)

def play_access_granted():
    if not BUZZER_ENABLED:
        return
    play_tone(392)  # G4
    play_tone(494)  # B4
    play_tone(587)  # D5
    play_tone(784, 0.2)  # G5

def play_access_denied():
    if not BUZZER_ENABLED:
        return
    play_tone(587)  # D5
    play_tone(494)  # B4
    play_tone(370, 0.3)  # F#4

def checkTag(reader):
    print("Bitte halte deine Karte bereit")
    id, text = reader.read()
    accepted, name = is_authorized(conn, id)
    if accepted:
        print(f"Ja cool komm rein, {name}") 
        GPIO.output(GLED, GPIO.HIGH)
        play_access_granted()  # Positive Melodie

        #Daten für die Datenbank vorbereiten
        Date = datetime.datetime.now()
        Event = "Zugang gewährt"
        User = id

        time.sleep(2)
        GPIO.output(GLED, GPIO.LOW)
        
        if conn.is_connected():  
            dbLog(conn, Date, Event, User)
        else:
            print("Datenbankverbindung nicht aktiv.") 
    else:
        print("du kommst hier nich rein!")
        GPIO.output(RLED, GPIO.HIGH)
        play_access_denied()  # Negative Melodie
        
        #Daten für die Datenbank vorbereiten
        Date = datetime.datetime.now()
        Event = "Zugang nicht gewährt"
        User = id

        time.sleep(2)
        if conn.is_connected():
            dbLog(conn, Date, Event, User)
        else:
            print("Datenbankverbindung nicht aktiv.")

#==========MAIN LOOP==========
def handle_admin_menu(name):
    while True:
        print("====================")
        print(f"Hallo {name}")
        print("Willkommen in der Admin übersicht.")
        input1 = input("Willst du tun?\n"
                      "1: Tag Lesen\n"
                      "2: Tag beschreiben\n"
                      "3: Eingang checken\n"
                      "4: Incidents überprüfen\n"
                      "5: Abmelden\n"
                      "Auswahl: ")
        
        actions = {
            "1": lambda: readTag(reader),
            "2": lambda: writeTag(reader),
            "3": lambda: checkTag(reader),
            "4": lambda: show_incidents(conn),
            "5": lambda: "exit"
        }
        
        if input1 in actions:
            result = actions[input1]()
            if result == "exit":
                return False, None, False
        else:
            print("Ungültige Eingabe. Bitte versuche es erneut.")
        
        print("====================")

def reset_gpio_config():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    # LED-Pins neu konfigurieren
    GPIO.setup(RLED, GPIO.OUT)
    GPIO.setup(YLED, GPIO.OUT)
    GPIO.setup(GLED, GPIO.OUT)

def beep(duration=0.5):
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def double_beep():
    beep(0.1)
    time.sleep(0.1)
    beep(0.1)

def test_buzzer():
    if not BUZZER_ENABLED:
        print("Buzzer ist deaktiviert")
        return
    setup_buzzer()
    print("Testing buzzer...")
    play_tone(440, 0.5)
    time.sleep(1)
    print("Test complete")

def main_loop():
    global didSetup
    
    # Buzzer initialisieren
    setup_buzzer()
    
    try:
        while True:
            # Initiales Setup oder Re-Setup nach RFID-Operationen
            if sensorSetup and not didSetup:
                reset_gpio_config()  # GPIO zurücksetzen
                sensor.setup_motion_sensor(conn)
                didSetup = True
                continue

            # Warten auf RFID-Tag
            status = None
            while status != reader2.MI_OK:
                (status, TagType) = reader2.MFRC522_Request(reader2.PICC_REQIDL)
                if status == reader2.MI_OK:
                    try:
                        didSetup = False  # Reset Setup-Flag vor RFID-Operation
                        # Admin-Check
                        isAdmin, name = readAdmin(reader)
                        if isAdmin and AdminSetup:
                            isAdmin, status, didSetup = handle_admin_menu(name)
                        else:
                            checkTag(reader)
                            
                    except KeyboardInterrupt:
                        print("Programm manuell angehalten")
                        GPIO.cleanup()
                        return
                        
                    except Exception as e:
                        print(f"FEHLER: {str(e)}")
                        GPIO.cleanup()
                        return
                        
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    #test_buzzer()  # Test ausführen
    main_loop()