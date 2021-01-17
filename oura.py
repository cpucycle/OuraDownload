import requests  # for getting URL
import json  # for parsing json
from datetime import datetime  # datetime parsing
from datetime import timedelta
import pytz  # timezone adjusting
import os
import dateutil.parser
from os import listdir
from os.path import isfile, join
import re


# A dictionary of data by date
bydate = {}
end_date = '2029-12-31'
start_date = '2000-01-01'

# There is obne activity per date
def handle_activity(data):
	for activity in data:
		if not 'summary_date' in activity:
			print('summary_date not found for activity')
		else:
			date = activity['summary_date']
			if date > start_date:
				if not date in bydate:
					bydate[date] = {}
				if 'activity' in bydate[date]:
					print(f'More than one activity found for {date}.')
				bydate[date]['activity'] = activity

# There is one bedtime per date
def handle_bedtime(data):
	for bedtime in data:
		if not 'date' in bedtime:
			print('date not found for ideal_bedtime')
		else:
			date = bedtime['date']
			if date > start_date:
				if not date in bydate:
					bydate[date] = {}
				if 'ideal_bedtime' in bydate[date]:
					print(f'More than one ideal_bedtime found for {date}.')
				bydate[date]['ideal_bedtime'] = bedtime

# There is zero or n sleep per date
def handle_sleep(data):
	for sleep in data:
		if not 'bedtime_end' in sleep:
			print('bedtime_end not found for sleep')
		else:
			date = dateutil.parser.parse(sleep['bedtime_end']).strftime("%Y-%m-%d")
			if date > start_date:
				if not date in bydate:
					bydate[date] = {}
				if not 'sleep' in bydate[date]:
					bydate[date]['sleep'] = []
				bydate[date]['sleep'].append(sleep)

# There is zero or n readiness per date, one for each sleep
def handle_readiness(data):
	for readiness in data:
		if not 'summary_date' in readiness:
			print('summary_date not found for readiness.')
		else:
			date = (dateutil.parser.parse(readiness['summary_date']) + timedelta(days=1)).strftime("%Y-%m-%d")
			if date > start_date:
				if not date in bydate:
					bydate[date] = {}
				if not 'readiness' in bydate[date]:
					bydate[date]['readiness'] = []
				bydate[date]['readiness'].append(readiness)

# Handle the data depending on the type
def handle(data):
	for key, value in data.items():
		if key == "activity":
			handle_activity(value)
		elif key == "ideal_bedtimes":
			handle_bedtime(value)
		elif key == "readiness":
			handle_readiness(value)
		elif key == "sleep":
			handle_sleep(value)
		else:
			print(f'Unknown data type {key}.')


#################################################################
# USER VARIABLES

save_directory = 'directory where files will be stored'
token = 'go to https://cloud.ouraring.com/personal-access-tokens to get yours'
try:
	config = {}
	with open(f'config') as f:
		config = json.load(f)
	if 'token' in config:
		token = config['token']
	if 'save_directory' in config:
		save_directory = config['save_directory']
except FileNotFoundError as e:
	print('Creating default config file. Edit that file and try again.')
	config = {}
	config['token'] = token
	config['save_directory'] = save_directory
	with open('config', 'w') as f:
		json.dump(config, f)
	exit()

# check the token
if not re.match('[0-9A-Z]{22}', token):
	print(f'The token is probably invalid.')
	exit()

# check the path
save_directory = save_directory.rstrip('\\')
if not os.path.isdir(save_directory):
	print(f'The save_directory "{save_directory} is not found.')
	exit()
save_directory = save_directory + '/'


#################################################################
# REQUEST VARIABLES

url = 'https://api.ouraring.com/v1/'
headers={"Authorization": f'Bearer {token}'}


#################################################################
# GET USER DATA

print(f'Checking {url}...')
r = requests.get(f'{url}userinfo', headers=headers)

# Exit if fail
if r.status_code != 200:
    print("Fail - Credentials rejected.")
    exit()

user_data = r.json()
if 'email' in user_data:
	print(f'  email: {user_data["email"]}')
if 'gender' in user_data:
	print(f'  gender: {user_data["gender"]}')
if 'age' in user_data:
	print(f'  age: {user_data["age"]}')
if 'weight' in user_data:
	print(f'  weight: {user_data["weight"]}kg')
if 'height' in user_data:
	print(f'  height: {user_data["height"]}cm')

#################################################################
# DETERMINE THE DATE RANGE FOR THE QUERY

# Get the file with the newest date in the directory, and start at the previous day
pattern = re.compile("^oura_[0-9]{4}-[0-9]{2}-[0-9]{2}.json$")
ourafiles = [f for f in listdir(save_directory) if isfile(join(save_directory, f)) and pattern.match(f)]
oldest = ''
for file in ourafiles:
	if file > oldest:
		oldest = file
if oldest:
	start_date = (datetime.strptime(oldest, 'oura_%Y-%m-%d.json') - timedelta(days=2)).strftime('%Y-%m-%d')

print(f'Getting files since {start_date}:')


#################################################################
# GET SLEEP DATA

params = {
    'start': f'{start_date}',
    'end': f'{end_date}'
}
summaries = ['activity', 'bedtime', 'sleep', 'readiness']

# Get the data by type
for summary in summaries:

	# Do an http GET for this summary
	print(f'  Getting {summary}...')
	response = requests.get(f'{url}{summary}', params=params, headers=headers)

	# Exit if fail
	if response.status_code != 200:
	    print("Fail - User ID / auth token rejected.")
	    exit()

	# Get the raw json from the response
	raw_data = response.json()

	# Save the raw_data to a file
	#with open(f'{save_directory}oura_{summary}.json', 'w') as outfile:
	#    json.dump(raw_data, outfile)

	# Get the raw_data from a file
	#with open(f'{save_directory}oura_{summary}.json') as f:
	#	 raw_data = json.load(f)

	# Handle the raw data, pulling it apart by date
	handle(raw_data)

# Dump the output to files by date
for date, value in bydate.items():
	outname = f'{save_directory}oura_{date}.json'

	# Try to get current contents
	try:
		with open(outname) as testfile:
			existing = json.load(testfile)
	except FileNotFoundError as e:
		existing = ''			
	except json.decoder.JSONDecodeError as e:
		print(f'ERROR: Unable to parse {outname}.')
		existing = ''

	# If different, then save the new version
	if existing != value: 
		with open(outname, 'w') as outfile:
			json.dump(value, outfile)
			if not existing:
				print(f'Saved {outname}')
			else:
				print(f'Updated {outname}')

# Finished
print('Finished.')
