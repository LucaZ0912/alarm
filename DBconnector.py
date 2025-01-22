import mysql.connector
from mysql.connector import Error
import datetime

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "",
            database = "alarm_system"
        )
        if conn.is_connected():
            print(f"Verbindung zur Datenbank erfolgreich")
            return conn, True
    except:
        print(f"Fehler beim Verbinden: {e}")
        return None, False
    

def is_authorized(conn, testID):
    try:
        cursor = conn.cursor()

        query = "SELECT name FROM user WHERE rfid = %s"
        cursor.execute(query, (testID,))

        result = cursor.fetchone()
        cursor.close

        if result:
            return True, result[0]
        else:
            return False, None 

    except:
        print(f"Fehler beim Abrufen der Daten: {err}")
        return False, None
    

def is_admin(conn, testID):
    try:
        cursor = conn.cursor()

        query = "SELECT name FROM user WHERE rfid = %s AND rolle = 'admin'"
        cursor.execute(query, (testID,))

        result = cursor.fetchone()
        cursor.close

        if result:
            return True, result[0]
        else:
            return False, None 

    except:
        print(f"Fehler beim Abrufen der Daten: {err}")
        return False, None

def dbLog(conn, Date, Event, User):
    try:
        print(Date, Event, User)
        cursor = conn.cursor()
        query = "INSERT INTO incidents (date, event, user) VALUES (%s, %s, %s)"
        print(query)
        data =  (Date, Event, User)
        data = (data[0].replace(microsecond=0), data[1], data[2])
        print(data)
        print("hallo")
        cursor.execute(query, data)
        conn.commit()
        print("Erfolgreich hochgeladen")

    except:
        print(f"Fehler beim Schreiben der Daten auf die Datenbank 'lol':")

def show_incidents(con):
    # Anzahl Zeilen vom Nutzer abfragen
    limit_str = input("Wie viele Zeilen aus 'incidents' sollen angezeigt werden? ")
    try:
        limit = int(limit_str)
    except ValueError:
        print("Ungültige Eingabe. Bitte eine ganze Zahl eingeben.")
        return

    # Datenbankabfrage mit LIMIT
    cursor = con.cursor()
    query = f"SELECT id, date, event, user FROM incidents ORDER BY id DESC LIMIT {limit}"
    cursor.execute(query)
    rows = cursor.fetchall()
    # Falls keine Einträge
    if not rows:
        print("Keine Einträge vorhanden oder Tabelle leer.")
    else:
        print(f"----- Letzte(n) {limit} Eintrag/Einträge in 'incidents' -----")
        for row in rows:
            print(f"ID: {row[0]}, Date: {row[1]}, Event: {row[2]}, User: {row[3]}")
        print("-------------------------------------------------------------")

    cursor.close()


