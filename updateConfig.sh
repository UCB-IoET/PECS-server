screen -S chairDriver -X quit
screen -S portServer -X quit
screen -d -m -S chairDriver twistd -n smap chair.ini
screen -d -m -S portServer python portServer.py
