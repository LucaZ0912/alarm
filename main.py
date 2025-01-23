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
sensorSetup = False
AdminSetup = True

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

def checkTag(reader): #Checkt ob der Benutzer zugriff zum Raum hat
    print("Bitte halte deine Karte bereit")
    id, text = reader.read()
    accepted, name = is_authorized(conn, id) #Gibt TRUE und den Namen zurück, wenn die ID in der Users Datenbank vorhanden ist.
    global status
    if accepted:
        print(f"Ja cool komm rein, {name}") 
        GPIO.output(GLED, GPIO.HIGH)

        #Daten für die Datenbank vorbereiten
        Date = datetime.datetime.now()
        Event = "Zuganggewaehrt"
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
        
        #Daten für die Datenbank vorbereiten
        Date = datetime.datetime.now()
        Event = "Zugang nicht gewaehrt"
        User = id

        #print(Date, Event, User)
        time.sleep(2)
        GPIO.output(RLED, GPIO.LOW)
        if conn.is_connected():  # Bei MySQL, für andere Datenbanken siehe jeweilige Dokumentation
            dbLog(conn, Date, Event, User)
        else:
            print("Datenbankverbindung nicht aktiv.") #Speichert das Event in der Incidents Datenbank
    
#==========MAIN LOOP==========
if sensorSetup:
    sensor.setup_motion_sensor(conn)
while True:
    status = None
    while status != reader2.MI_OK:
        (status,TagType) = reader2.MFRC522_Request(reader2.PICC_REQIDL)
        if status == reader2.MI_OK:
            try:
                idTest, name = readAdmin(reader) #Bekommt TRUE (Bei Admin) oder FALSE wieder
                if idTest and AdminSetup: #Wenn die Datenbank ein True zurück gebt und die Einstellung AdminSetUp true ist.
                    isAdmin = True #Wenn Admin wird eine oberfläche zur Auswahl getriggert
                    while isAdmin:
                        input1 = None
                        print("====================")
                        print(f"Hallo {name}")
                        print("Willkommen in der Admin übersicht.")
                        input1 = input("Willst du tun? Tag Lesen (1) / Tag beschreiben (2) / Eingang checken (3) / Incidents überprüfen (4) abmelden (5) ")
                        time.sleep(1)
                        #print("Dein Input ist:")
                        print(input1)
                        if input1 == "1":
                            print("Lesemodul aktiv")
                            print("halte das Tag an das Lesegerät")
                            time.sleep(0.1)
                            readTag(reader)
                            print("====================")
                        elif input1 == "2":
                            writeTag(reader)
                            print("====================")
                        elif input1 == "3":
                            checkTag(reader)
                            print("====================")
                        elif input1 == "4":
                            print(f"Auf Widersehen {name}")
                            print("====================")
                            isAdmin = False
                            status = None
                        elif input1 == "5":
                            show_incidents(conn)
                        else:
                            print("ich konnte deinen Input nicht zuordnen. Bitte versuche es erneut")
                else:
                    checkTag(reader)
                    
            except KeyboardInterrupt:
                print("Programm manuell angehalten")
                GPIO.cleanup()
            
            except:
                print("FEHLER!!!")
                GPIO.cleanup()
                
            finally:
                GPIO.cleanup()
        


            
                
            
   
    
    
