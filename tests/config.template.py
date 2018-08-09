# get this from firebase console
# go to project settings, general tab and click "Add Firebase to your web app"
SIMPLE_CONFIG = {
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "storageBucket": "",
}

# get this json file from firebase console
# go to project settings, service accounts tab and click generate new private key
SERVICE_ACCOUNT_PATH = "secret.json"

SERVICE_CONFIG = dict(SIMPLE_CONFIG, serviceAccount=SERVICE_ACCOUNT_PATH)
