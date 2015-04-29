import json
from smap import actuate, driver, util
from chairActuator import ChairHeaterActuator
import time
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

readings = {
    "backh": 0,
    "bottomh": 0,
    "backf": 0,
    "bottomf": 0,
    "occupancy": 0,
    "temperature": 0.0,
    "humidity": 0.0
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
        self.state = readings.copy()
        backh = self.add_timeseries('/backheater', '%', data_type='long')
        bottomh = self.add_timeseries('/bottomheater', '%', data_type='long')
        backf = self.add_timeseries('/backfan', '%', data_type='long')
        bottomf = self.add_timeseries('/bottomfan', '%', data_type='long')
        occ = self.add_timeseries('/occupancy', 'binary', data_type='long')
        temp = self.add_timeseries('/temperature', 'Celsius', data_type='double')
        hum = self.add_timeseries('/humidity', '%', data_type='double')
        #self.add_actuator('/heateract', 'Heater Setting', klass=ChairHeaterActuator, setup={'filename': 'hello'}, read_limit=1, write_limit=1)
        #self.set_metadata('/heateract', {'actuatable': 'true'})
        
        archiver = opts.get('archiver')
        backh.add_actuator(ChairActuator(chair=self, key="backh", archiver=archiver))
        bottomh.add_actuator(ChairActuator(chair=self, key="bottomh", archiver=archiver))
        backf.add_actuator(ChairActuator(chair=self, key="backf", archiver=archiver))
        bottomf.add_actuator(ChairActuator(chair=self, key="bottomf", archiver=archiver))


        self.port = int(opts.get('port', 9001))

    def start(self):
        util.periodicSequentialCall(self.poll).start(5)
        reactor.listenTCP(self.port, factory)
        reactor.run()

    def poll(self):
        self.state = readings.copy()
        currTime = time.time()
        self.add('/backheater', currTime, readings['backh'])
        self.add('/bottomheater', currTime, readings['bottomh'])
        self.add('/backfan', currTime, readings['backf'])
        self.add('/bottomfan', currTime, readings['bottomf'])
        self.add('/occupancy', currTime, 1 if readings['occupancy'] else 0)
        self.add('/temperature', currTime, readings['temperature'])
        self.add('/humidity', currTime, readings['humidity'])

class ChairActuator(actuate.ContinuousIntegerActuator):
    def __init__(self, **opts):
        datarange = (0, 100)
        actuate.SmapActuator.__init__(self, archiver_url=opts['archiver'])
        actuate.ContinuousIntegerActuator.__init__(self, datarange)
        self.chair = opts['chair']
        self.key = opts['key']

    def get_state(self, request):
        return self.chair.state[self.key]

    def set_state(self, request, state):
        if not self.valid_state(state):
            print "WARNING: attempt to set to invalid state", state
            return self.chair.state[self.key]
        self.chair.state[self.key] = self.parse_state(state)
        print "Setting", self.key, "to", state
        return int(state)
