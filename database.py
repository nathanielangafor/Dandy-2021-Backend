import json
import sqlite3
import base64
import random
from google.cloud import storage
import string
from PIL import Image
from io import BytesIO
import os
from flask import Flask, request
app = Flask(__name__)
app.secret_key = b"Da ya biezlikiy patamy shto u menya nie litso"

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/nangafor/Dandy-2021-Backend/engaged-diode-329906-957b934a14a8.json'

def readOne(table, criteria, value):
    conn = sqlite3.connect("database.db")

    c = conn.cursor()
    c.execute('SELECT * FROM {} WHERE {}=(?)'.format(table, criteria), (value,))
    data = c.fetchone()
    return json.dumps(data)

def orig_read(table):
    conn = sqlite3.connect("database.db")

    c = conn.cursor()
    c.execute('SELECT * FROM {}'.format(table))
    data = c.fetchall()
    return json.dumps(data)

def get_blob_link(bucket_name, source_file_name):

    storage_client = storage.Client("Dandy Bois")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_file_name)

    blob.make_public()
    url = blob.public_url

    return url


def upload_blob(bucket_name, source_file_name, destination_blob_name):

    storage_client = storage.Client("Dandy Bois")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

def randomString(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def userTable():
    conn = sqlite3.connect("database.db")

    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS Users (email TEXT, username TEXT, password TEXT, points INETEGER, achievements TEXT)')

def locationTable():
    conn = sqlite3.connect("database.db")

    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS Locations (id INTEGER, user TEXT, longitude REAL, latitude REAL, image TEXT, comment TEXT, type INTEGER, title TEXT, currentUser TEXT, points INTEGER, locName STRING)')

@app.route('/update/', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        conn = sqlite3.connect("database.db")


        parsed = json.loads((request.data).decode('utf-8')) 

      
        c = conn.cursor()
        c.execute('UPDATE {} SET {}=(?) WHERE {}=(?)'.format(parsed['form']['table'], parsed['form']['setPos'], parsed['form']['where']), (parsed['form']['newValue'], parsed['form']['whereValue'],))
        conn.commit()

        return 'True'

@app.route('/insertUser/', methods=['GET', 'POST'])
def insertUser():
    if request.method == 'POST':
        conn = sqlite3.connect("database.db")

        achievements = {
            "beHuman": ["Be Human", False, "You are human!", 100],
            "environmentalist": ["Environmentalist", False, "You completed your first cleanup activity!", 100],
            "warrior": ["Warrior", False, "You completed your first 5 cleanup activities!", 300],
            "cleanupWarlock": ["Cleanup Warlock", False, "You completed your first 10 cleanup activities!", 500],
        }
            
        points = 0

        c = conn.cursor()
        c.execute("INSERT INTO Locations (id, user, longitude, latitude, image, comment, type, title, currentUser, points) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (len(orig_read('Locations')) + 1, parsed['user'], float(parsed['longitude']), float(parsed['latitude']), "", parsed['comment'], parsed['type'], parsed['title'], '', int(parsed['points']) ))
        conn.commit()   

        return 'True'

@app.route('/insertLocation/', methods=['GET', 'POST'])
def insertLocation():
    if request.method == 'POST':
        conn = sqlite3.connect("database.db")
        
        parsed = json.loads((request.data).decode('utf-8')) 
        
        try:

            fileName = randomString(9)
            image = Image.open(BytesIO(base64.b64decode(parsed['image'])))
            image.save('{}.png'.format(fileName), 'PNG')

            upload_blob("dbb_1", '{}.png'.format(fileName), '{}.png'.format(fileName))
            image = get_blob_link("dbb_1", "{}.png".format(fileName))

            print(image)

            c = conn.cursor()
            c.execute("INSERT INTO Locations (id, user, longitude, latitude, image, comment, type, title, currentUser, points, locName) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (len(orig_read('Locations')) + 1, parsed['user'], float(parsed['longitude']), float(parsed['latitude']), image, parsed['comment'], parsed['type'], parsed['title'], '', int(parsed['points']), parsed['locName']))
            conn.commit()

            os.remove(fileName + '.png')
            
        except:
            c = conn.cursor()
            c.execute("INSERT INTO Locations (id, user, longitude, latitude, image, comment, type, title, currentUser, points, locName) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (len(orig_read('Locations')) + 1, parsed['user'], float(parsed['longitude']), float(parsed['latitude']), parsed['image'], parsed['comment'], parsed['type'], parsed['title'], '', int(parsed['points']), parsed['locName']))
            conn.commit()

        return 'True'

@app.route('/delete/', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        conn = sqlite3.connect("database.db")
        
        parsed = json.loads((request.data).decode('utf-8')) 

        c = conn.cursor()
        c.execute('DELETE FROM {} WHERE {}=(?)'.format(parsed['table'], parsed['criteria']), (parsed['identifier'],))
        conn.commit()

        return 'True'

@app.route('/read/', methods=['GET', 'POST'])
def read():
    if request.method == 'POST':
        
        parsed = json.loads((request.data).decode('utf-8'))
        
        print(parsed)
        
        return str(orig_read(parsed['table']))


@app.route('/readOne/', methods=['GET', 'POST'])
def readOne1():
    if request.method == 'POST':
        
        parsed = json.loads((request.data).decode('utf-8')) 
        data = str(readOne(parsed['user']['table'], parsed['user']['criteria'], parsed['user']['value']))

        return data


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect("database.db")

        c = conn.cursor()
        c.execute('SELECT * FROM Users')
        data = c.fetchall()

        for user in data:
            if user[1] == request.form.get('username'):
                if user[2] == request.form.get('password'):
                    return 'logged in'
                else:
                    return 'invalid password'

        return 'invalid username'


@app.route('/test/', methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        return 'TEST'

userTable()
locationTable()


if __name__ == "__main__":
    app.run(host= '0.0.0.0', port="80")

