#!/bin/bash
screen -S chairDriver -X quit
screen -S portServer -X quit
screen -S actuateServer -X quit
screen -S udpReportingServer -X quit
screen -d -m -S chairDriver twistd -n smap chair.ini
screen -d -m -S portServer python portServer.py
screen -d -m -S actuateServer python actuateServer.py
screen -d -m -S udpReportingServer python udp_reporting_server.py
