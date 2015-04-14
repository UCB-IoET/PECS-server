import json
from smap import driver, util
from chairActuator import ChairHeaterActuator
import time
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

readings = {
    "backHeater": 0,
    "bottomHeater": 0,
    "backFan": 0,
    "bottomFan": 0,
    "occupancy": 0
}

translator = {
    "OFF": 0,
    "ON": 100,
    "LOW": 25,
    "MEDIUM": 50,
    "HIGH": 75,
    "MAX": 100
}

class ChairResource(Resource):
    isLeaf = True
    def render_GET(self, request):
        return '<html>Chair data receiver</html>'
    def render_POST(self, request):
        doc_recvd = request.content.read()
        print doc_recvd
        doc = json.loads(doc_recvd)
        for key in doc:
            if key in readings:
                readings[key] = doc[key]
            elif key == "heaters":
                readings["bottomHeater"] = doc[key]
                readings["backHeater"] = doc[key]
            elif key == "fans":
                readings["bottomFan"] = doc[key]
                readings["backFan"] = doc[key]
        return 'okay'

factory = Site(ChairResource())

class PECSChairDriver(driver.SmapDriver):
    def setup(self, opts):
        self.add_timeseries('/backheater', '%', data_type='long')
        self.add_timeseries('/bottomheater', '%', data_type='long')
        self.add_timeseries('/backfan', '%', data_type='long')
        self.add_timeseries('/bottomfan', '%', data_type='long')
        self.add_timeseries('/occupancy', 'binary', data_type='long')
        #self.add_actuator('/heateract', 'Heater Setting', klass=ChairHeaterActuator, setup={'filename': 'hello'}, read_limit=1, write_limit=1)
        #self.set_metadata('/heateract', {'actuatable': 'true'})
        self.port = int(opts.get('port', 9001))

    def start(self):
        util.periodicSequentialCall(self.poll).start(5)
        reactor.listenTCP(self.port, factory)
        reactor.run()

    def poll(self):
        currTime = time.time()
        self.add('/backheater', currTime, readings['backHeater'])
        self.add('/bottomheater', currTime, readings['bottomHeater'])
        self.add('/backfan', currTime, readings['backFan'])
        self.add('/bottomfan', currTime, readings['bottomFan'])
        self.add('/occupancy', currTime, 1 if readings['occupancy'] else 0)
