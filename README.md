# Oura ring daily data download
This project will save oura sleep, readiness, and activity data to daily json files. The intent 
is to use this script alongside another application that scans the directory for modified files 
and imports them into the app.

1. Clone this repo.
2. Make the script executable:
```
chmod +x oura.sh
```
3. Get your personal access token from [Oura Ring Developer](https://cloud.ouraring.com/personal-access-tokens).
4. Edit the config file in this directory, and set your token and save_directory.
5. Create the save_directory if it doesn't exist yet.
6. Run the script as needed/wanted:
```
./oura.sh
```
