from firebase import firebase
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL")

if not FIREBASE_DATABASE_URL:
    raise Exception("Firebase database URL not found in .env file")

# Initialize Firebase
firebase_app = firebase.FirebaseApplication(FIREBASE_DATABASE_URL, None)

def save_token(user_id, token):
    result = firebase_app.put(f'/userTokens/{user_id}', 'token', token)
    return result

def get_token(user_id):
    result = firebase_app.get(f'/userTokens/{user_id}', 'token')
    return result or {}
