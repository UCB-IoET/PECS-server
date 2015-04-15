import json
import msgpack
import requests
import socket

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.bind(('', 38003))

while True:
    data = sock.recv(1024)
    received = msgpack.unpackb(data)
    jsonData = json.dumps(received)
    print "Received:", jsonData
    r = requests.post("http://localhost:38001", data=jsonData)
    print r.text
