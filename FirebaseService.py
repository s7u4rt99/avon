import pyrebase
from dotenv import load_dotenv
import os

load_dotenv()

FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN")
FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL")
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET")
FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID")
FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID")

if not all([FIREBASE_API_KEY, FIREBASE_AUTH_DOMAIN, FIREBASE_DATABASE_URL, FIREBASE_PROJECT_ID, FIREBASE_STORAGE_BUCKET, FIREBASE_MESSAGING_SENDER_ID, FIREBASE_APP_ID]):
    raise Exception("Firebase data not found in .env file")

config = {
  "apiKey": FIREBASE_API_KEY,
  "authDomain": FIREBASE_AUTH_DOMAIN,
  "databaseURL": FIREBASE_DATABASE_URL,
  "projectId": FIREBASE_PROJECT_ID,
  "storageBucket": FIREBASE_STORAGE_BUCKET,
  "messagingSenderId": FIREBASE_MESSAGING_SENDER_ID,
  "appId": FIREBASE_APP_ID
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()

def save_token(user_id, token):
    values = db.child("userTokens").child(user_id).get().val() or {}
    payload = {**values, "token": token}
    db.child("userTokens").child(user_id).set(payload)

def get_token(user_id):
    values = db.child("userTokens").child(user_id).get().val()
    return values or {}

