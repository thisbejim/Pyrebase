import os

SIMPLE_CONFIG = {
    # "apiKey": "",
    # "authDomain": "",
    # "databaseURL": "",
    # "storageBucket": "",
    "apiKey" : "AIzaSyB7OkrIN01JHaXoy-BLzf131iaN2DGqFWY",
    "authDomain" : "talli-development.firebaseapp.com",
    "databaseURL" : "https://talli-development.firebaseio.com",
    "projectId" : "talli-development",
    "storageBucket" : "talli-development.appspot.com",
    "messagingSenderId" : "25240239942"
}

with open("secret.json",'w') as f:
    f.write(os.environ["FIREBASE_JSON"])

SERVICE_ACCOUNT_PATH = "secret.json"

SERVICE_CONFIG = dict(SIMPLE_CONFIG, serviceAccount=SERVICE_ACCOUNT_PATH)
