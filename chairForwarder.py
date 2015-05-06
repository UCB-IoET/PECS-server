import json
import msgpack
import requests
import socket

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.bind(('', 38003))

while True:
    data, addr = sock.recvfrom(1024)
    received = msgpack.unpackb(data)
    newmsg = {}
    newmsg['macaddr'] = hex(received[1])[-4:]
    newmsg['occupancy'] = received[2]
    newmsg['backh'] = received[3]
    newmsg['bottomh'] = received[4]
    newmsg['backf'] = received[5]
    newmsg['bottomf'] = received[6]
    newmsg['temperature'] = received[7]
    newmsg['humidity'] = received[8]
    newmsg['fromFS'] = True
    newmsg['myIP'] = addr[0]
    jsonData = json.dumps(newmsg)
    print "Received:", jsonData
    r = requests.post("http://localhost:38001", data=jsonData)
    print r.text
