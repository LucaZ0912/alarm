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

def dbLog(conn, Date, Event, User, Picpath):
    try:
        print(Date, Event, User, Picpath)
        cursor = conn.cursor()
        query = "INSERT INTO incidents (date, event, user, picpath) VALUES (%s, %s, %s, %s)"
        print(query)
        data =  (Date, Event, User, Picpath)
        data = (data[0].replace(microsecond=0), data[1], data[2], data[3])
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

def get_events(limit=50):
    conn = get_db_connection()[0]
    cursor = conn.cursor()
    
    if limit is None:
        # Wenn kein Limit gesetzt ist, hole alle Events ohne LIMIT-Klausel
        cursor.execute('''
            SELECT date, event, user 
            FROM incidents 
            ORDER BY date DESC
        ''')
    else:
        # Mit Limit
        cursor.execute('''
            SELECT date, event, user 
            FROM incidents 
            ORDER BY date DESC 
            LIMIT %s
        ''', (limit,))
    
    events = cursor.fetchall()
    conn.close()
    return events

def get_events_by_type(event_types, limit=5):
    conn = get_db_connection()[0]
    cursor = conn.cursor()
    
    # Erstelle den IN-Operator mit der richtigen Anzahl von Platzhaltern
    placeholders = ', '.join(['%s'] * len(event_types))
    query = f'''
        SELECT date, event, user 
        FROM incidents 
        WHERE event IN ({placeholders})
        ORDER BY date DESC 
        LIMIT %s
    '''
    
    # Füge limit als letzten Parameter hinzu
    params = list(event_types) + [limit]
    cursor.execute(query, params)
    
    events = cursor.fetchall()
    conn.close()
    return events


