# save this as app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from functools import wraps
import sqlite3
from DBconnector import get_db_connection, get_events, get_events_by_type
import subprocess
import os
import signal
import RPi.GPIO as GPIO
import time

app = Flask(__name__)
app.secret_key = 'dein_geheimer_schluessel_hier'  # Wichtig für Sessions

# Login-Decorator für geschützte Routen
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Globale Variable für den Prozess
alarm_process = None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        
        try:
            conn = get_db_connection()[0]
            if conn is None:
                flash('Datenbankverbindung konnte nicht hergestellt werden!')
                return render_template('login.html')
            
            cursor = conn.cursor()
            
            # Debug-Ausgaben
            print(f"Versuche Login mit ID: {user_id} und Passwort: {password}")
            
            # MySQL-spezifische SQL-Abfrage mit %s als Platzhalter
            sql = "SELECT * FROM user WHERE id=%s AND password=%s"
            params = (user_id, password)
            print(f"SQL: {sql}")
            print(f"Parameter: {params}")
            
            cursor.execute(sql, params)
            user = cursor.fetchone()
            
            if user:
                print(f"Gefundener Benutzer: {user}")
                session['user_id'] = user_id
                conn.close()
                return redirect(url_for('dashboard'))
            else:
                print("Kein Benutzer gefunden")
                flash('Ungültige Anmeldedaten!')
            
            conn.close()
            
        except Exception as e:
            print(f"Datenbankfehler: {str(e)}")
            print(f"Typ des Fehlers: {type(e)}")
            flash('Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Hole die letzten Events aus der Datenbank
    events = get_events()
    return render_template('dashboard.html', events=events)

@app.route('/toggle_alarm', methods=['POST'])
@login_required
def toggle_alarm():
    global alarm_process
    
    if alarm_process is None or alarm_process.poll() is not None:
        # Starte main.py
        try:
            alarm_process = subprocess.Popen(['python3', 'main.py'])
            return {'status': 'armed'}
        except Exception as e:
            print(f"Fehler beim Starten: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    else:
        # Stoppe main.py
        try:
            alarm_process.terminate()
            alarm_process.wait(timeout=5)  # Warte bis zu 5 Sekunden auf Beendigung
            alarm_process = None
            return {'status': 'disarmed'}
        except Exception as e:
            print(f"Fehler beim Stoppen: {str(e)}")
            return {'status': 'error', 'message': str(e)}

@app.route('/alarm_status')
@login_required
def alarm_status():
    global alarm_process
    if alarm_process is None or alarm_process.poll() is not None:
        return {'status': 'disarmed'}
    return {'status': 'armed'}

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/get_events')
@login_required
def get_events_json():
    # Hole Events nach Typ sortiert
    access_events = get_events_by_type(['Zugang gewährt', 'Zugang nicht gewährt'], 5)
    motion_events = get_events_by_type(['Bewegung festgestellt'], 5)
    barrier_events = get_events_by_type(['Lichtschranke aktiviert'], 5)
    
    return jsonify({
        'access': list(access_events),
        'motion': list(motion_events),
        'barrier': list(barrier_events)
    })

@app.route('/full_incidents')
@login_required
def full_incidents():
    sort = request.args.get('sort', 'date')  # Standard-Sortierung nach Datum
    order = request.args.get('order', 'desc')  # Standard-Reihenfolge absteigend
    
    try:
        conn = get_db_connection()[0]
        cursor = conn.cursor()
        
        # SQL-Query mit dynamischer Sortierung
        order_direction = "DESC" if order == 'desc' else "ASC"
        if sort == 'event':
            sql = f"SELECT date, event, user FROM incidents ORDER BY event {order_direction}, date DESC"
        elif sort == 'user':
            sql = f"SELECT date, event, user FROM incidents ORDER BY user {order_direction}, date DESC"
        else: # sort == 'date'
            sql = f"SELECT date, event, user FROM incidents ORDER BY date {order_direction}"
            
        cursor.execute(sql)
        incidents = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Bestimme die umgekehrte Sortierrichtung für die Links
        reverse_order = 'asc' if order == 'desc' else 'desc'
        
        return render_template('full_incidents.html', 
                             incidents=incidents, 
                             current_sort=sort, 
                             current_order=order,
                             reverse_order=reverse_order)
    except Exception as e:
        print(f"Fehler beim Abrufen der Vorfälle: {str(e)}")
        return render_template('full_incidents.html', incidents=[])

@app.route('/users')
@login_required
def users():
    conn = get_db_connection()[0]
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, rfid, rolle FROM user')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/options')
@login_required
def options():
    return render_template('options.html')

@app.route('/bilder', endpoint='pictures_here')
def show_images():
    image_folder = '/home/it/it/captures'
    image_files = sorted([f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))])
    return render_template('pictures_here.html', images=image_files)

# Route, um einzelne Bilder aus dem Ordner bereitzustellen
@app.route('/captures/<filename>')
def get_image(filename):
    return send_from_directory('/home/it/it/captures', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')