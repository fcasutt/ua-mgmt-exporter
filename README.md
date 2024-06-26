# Google Universal Analytics Settings Exporter
The aim of this exporter is to get an archive of all Accounts, Propertis and Views with the corresponding IDs and settings for future reference (e.g. was Filter X Active on View Y?)

The script will store the settings retrieved via API into multiple csv files. These will be placed in a timestamped subfolder in the /output/ folder.

# Set Up OAuth 2.0 Credentials:

Go to the Google Cloud Console.
Select your project or create a new one.
Navigate to APIs & Services > Credentials.
Click on Create credentials > OAuth client ID.
Configure the consent screen if you haven't done so already.
Choose Desktop app as the application type.
Download the JSON file with the client ID and client secret.


# Prerequesits:
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas


# Instructions:
Replace path/to/client_secret.json with the actual path to your client_secret.json file.
Ensure you have the required Python packages installed.
Run the script: python download_analytics_settings.py
