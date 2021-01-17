#!/usr/bin/env bash

readonly sourceFile="./env/bin/activate"

# If env/bin/activate does net yet exist, then create the virtual environment and install some python packages
if [ ! -f "$sourceFile" ]; then
	echo Creating a python virtual environment...
	python3 -m venv env
	source env/bin/activate
	pip install --upgrade pip
	pip install python-dateutil requests pytz
	deactivate 
	echo Done.
fi

# Activate the virtual environment, run the python script, and deactivate
source ${sourceFile}
python3 ./Oura.py
deactivate
