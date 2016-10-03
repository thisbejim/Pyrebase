SIMPLE_CONFIG = {
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "storageBucket": "",
}

SERVICE_ACCOUNT_PATH = "secret.json"

SERVICE_CONFIG = dict(SIMPLE_CONFIG, serviceAccount=SERVICE_ACCOUNT_PATH)
