#!/bin/bash

# Verify instalation of mopidy
if ! mopidy --version >/dev/null
then
	#Only works on ubuntu systems
	echo "Mopidy is not installed, installing mopidy with 'sudo apt-get install mopidy'"
	sudo apt-get install mopidy
fi

#Verify installation of python, not tested
if ! python3 --version >/dev/null
then
	#Only works on ubuntu systems, which generally comes with python pre-installed
	echo "Python is not installed, installing python3 with 'sudo apt-get install python3.6"
	sudo apt-get install python3.6
fi

#Verify installation of websocket
if !  pip show websocket >/dev/null
then
	echo "Websocket not installed, installing now"
	pip install websocket --user
	#Websocket-client needs to be installed AFTER websocket
	pip install websocket-client --user
fi

#Verify installation of websocket-client
if !  pip show websocket-client >/dev/null
then
	echo "Websocket-client not installed, installing now"
	pip install websocket --user
	pip install websocket-client --user
fi

#Start mopidy and after 5 seconds start main.py
mopidy & (sleep 5s && python3 main.py)
