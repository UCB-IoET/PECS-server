from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import ConfigParser
import json
import requests
import socket

APP_LINK = 'https://www.dropbox.com/s/rs9qprdnzo5mog6/chairtalk.apk?dl=1'
    
class DownloadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            agent = self.headers['user-agent']
            if 'Android' in agent:
                f = open(APK_FILE_NAME, 'rb')
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            elif 'iPhone' in agent:
                self.send_response(301)
                self.send_header('Location','https://www.apple.com')
                self.end_headers()
                return
        except:
            print "sending 400: invalid"
            self.send_response(400)
            return

serv = HTTPServer(('', 38003), DownloadHandler)
serv.serve_forever()
