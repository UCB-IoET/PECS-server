from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import ConfigParser
import json
import requests
import socket
import urlparse
from string import Template
import ConfigParser
from uuid import uuid4
import sqlite3

ID_KEY = 'chairid'
ANDROID_LINK = 'https://www.dropbox.com/s/rs9qprdnzo5mog6/chairtalk.apk?dl=1'
IOS_LINK = 'https://www.developer.apple.com'

DB_FILE = 'users.db'

parser = ConfigParser.RawConfigParser()
parser.read('chair.ini')
for sect in parser.sections():
    if parser.has_option(sect, 'db_file'):
        DB_FILE = parser.get(sect, 'db_file')
    elif parser.has_option(sect, 'android_url'):
        APP_LINK = parser.get(sect, 'android_url')

db = sqlite3.connect(DB_FILE)
cursor = db.cursor()
cursor.execute('''create table if not exists users (uuid TEXT PRIMARY KEY, chairid TEXT)''')
db.commit()
db.close()

PAGE_TEMPLATE = Template('''<!DOCTYPE HTML>
<html lang="en-US">
    <head>
        <!--DO NOT DELETE THE BELOW COMMENT-->
        <!--uuid:$uuid-->
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="1;url=$app_link">
        <script type="text/javascript">
            window.location.href = "$app_link"
        </script>
        <title>PECS Chair Setup</title>
    </head>
    <body>
        If you are not redirected automatically, follow the <a href='$app_link'>link to download app</a>
    </body>
</html>
''')

def add_new_user(chair_id):
    uuid = str(uuid4())
    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    try:
        cursor.execute('''INSERT INTO users(uuid, chairid)
                            VALUES(?,?)''', (uuid, chair_id))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return uuid

def get_users(chair_id):
    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute('''SELECT uuid FROM users WHERE chairid=?''', (chair_id,))
    all_rows = cursor.fetchall()
    print all_rows
    db.close()

def generate_page(chair_id, request):
    # return PAGE_TEMPLATE.safe_substitute(uuid=add_new_user(chair_id))
    agent = request.headers['user-agent']
    if 'Android' in agent:
        agent_sub = ANDROID_LINK
    else:
        agent_sub = IOS_LINK
    return PAGE_TEMPLATE.safe_substitute(uuid=uuid4(), app_link=agent_sub)
    
class InitializationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path, tmp = self.path.split('?', 1)
            qs = urlparse.parse_qs(tmp)
            chair_id = qs[ID_KEY]

        except:
            print "sending 400: invalid"
            self.send_response(400)
            return
        if ID_KEY in qs:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(generate_page(chair_id, self))
        else:
            print "sending 400: missing"
            self.send_response(400)
            return

serv = HTTPServer(('', 38002), InitializationHandler)
serv.serve_forever()
