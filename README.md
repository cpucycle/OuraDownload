# Oura ring daily data download
This project will save oura sleep, readiness, and activity data to daily json files. The intent 
is to use this script alongside another application that scans the directory for modified files 
and imports them into the app.

1. Clone this repo:
```
git clone https://github.com/cpucycle/OuraDownload.git
```
2. Change to the directory:
```
cd OuraDownload
```
3. Make the script executable:
```
chmod +x oura.sh
```
4. Get your personal access token from [Oura Ring Developer](https://cloud.ouraring.com/personal-access-tokens).
5. Edit the config file in this directory, and set your token and save_directory where you want it to store the files.
6. Create the save_directory if it doesn't exist yet.
7. Run the script as needed/wanted:
```
./oura.sh
```
