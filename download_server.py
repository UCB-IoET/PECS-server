from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import ConfigParser
import json
import requests
import socket

APK_FILE_NAME = "~/chairtalk.apk"
    
class DownloadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            agent = self.headers['user-agent']
            if 'Android' in agent:
                f = open(APK_FILE_NAME)
                data = f.read()
            elif 'iPhone' in agent:
                self.send_response(301)
                self.send_header('Location','https://www.apple.com')
                self.end_headers()
                return
        except:
            print "sending 400: invalid"
            self.send_response(400)
            return
        
            self.send_response(200)
            self.send_header('Content-type', 'application/zip')
            self.end_headers()
            self.wfile.write(data)
        else:
            print "sending 400: missing"
            self.send_response(400)
            return

serv = HTTPServer(('', 38003), DownloadHandler)
serv.serve_forever()
