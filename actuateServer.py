from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import ConfigParser
import json
import msgpack
import requests
import socket
import urlparse

settingMap = {
    "OFF": 0,
    "ON": 100,
    "LOW": 25,
    "MEDIUM": 50,
    "HIGH": 75,
    "MAX": 100
}

ipmap = {}

parser = ConfigParser.RawConfigParser()
parser.read('chair.ini')
for sect in parser.sections():
    if parser.has_option(sect, 'macaddr') and parser.has_option(sect, 'rel_ip') and parser.has_option(sect, 'dest_ip') and parser.has_option(sect, 'port'):
        ipmap[parser.get(sect, 'macaddr')] = (parser.get(sect, 'rel_ip'), parser.get(sect, 'dest_ip'), parser.get(sect, 'port'))

FS_PORT = 60001
    
class ActuationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path, tmp = self.path.split('?', 1)
            qs = urlparse.parse_qs(tmp)
            macaddr = qs['macaddr']
            ips = ipmap[macaddr[0]]
        except:
            print "sending 400: invalid"
            self.send_response(400)
            return
        if 'macaddr' in qs:
            res = requests.get("http://localhost:{0}/".format(ips[2]))
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(res.text)
        else:
            print "sending 400: missing"
            self.send_response(400)
            return

    def do_POST(self):
        doc_recvd = self.rfile.read(int(self.headers['Content-Length']))
        try:
            doc = json.loads(doc_recvd)
            macaddr = doc.pop('macaddr')
            ips = ipmap[macaddr]
        except:
            self.send_response(400)
            return
        res = requests.post("http://localhost:{0}/".format(ips[2]), json.dumps(doc))
        if res.status_code != 200:
            self.send_response(404)
            self.end_headers()
            self.wfile.write("Could not update sMAP")
            return
        print "Successfully updated sMAP"
        removeList = []
        timestamp = int(res.text)
        if 'fromIP' in doc:
            ips[0] = doc['fromIP']
        if 'myIP' in doc:
            ips[1] = doc['myIP']
        if 'fromFS' not in doc:
            for key in doc:
                if key not in ["backh", "bottomh", "backf", "bottomf", "heaters", "fans"]:
                    removeList.append(key)
            for key in removeList:
                del doc[key]
            if len(doc) != 0:
                doc["_id"] = 0 # Should we add RNQ functionality here?
                doc["toIP"] = ips[0]
                doc["time"] = timestamp
                if "header" in doc:
                    del doc["header"]
                sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                sock.bind(('', 38002))
                print "Actuating chair"
                sock.sendto(msgpack.packb(doc), (ips[1], FS_PORT))
                sock.close()
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        self.wfile.write(str(timestamp))

serv = HTTPServer(('', 38001), ActuationHandler)
serv.serve_forever()
