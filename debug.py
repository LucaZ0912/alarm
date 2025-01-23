#Dient dem lesen von Tags ohne Admintag (beispielsweise wenn nach dem Schulblock die alten Tags nicht mehr zur verfügung stehen)

import RPi.GPIO as GPIO
import mfrc522
import time
from mfrc522 import SimpleMFRC522
from mfrc522 import MFRC522
reader = SimpleMFRC522()
reader2 = MFRC522()

adminID = 628267626831



def writeTag(reader):
    text = input('Enter tag data:')
    print("Hold tag to module")
    reader.write(text)
    print("Done...")
            
def readTag(reader):
    id, text = reader.read()
    print(id)
    print(text)
def readAdmin(reader):
    id = reader.read()
    return id
def checkTag(reader):
    print("Bitte halte deine Karte bereit")
    id, text = reader.read()
    if id == 565666644585:
        print("Ja cool komm rein bro")
    else:
        print("du kommst hier nich rein!")
    

def debugLesen(reader):
    print("Willkommen im Debug Lesen Menü")
    print("halte deinen Tag an den Scanner")
    readTag(reader)

while True:
    debugLesen(reader)
        


            
                
            
   
    
    
