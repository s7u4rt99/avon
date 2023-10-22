from typing import TypedDict, Union, Optional
from firebase import firebase
from dotenv import load_dotenv
from datetime import datetime
import os
import uuid

import pytz

# Load environment variables
load_dotenv()

FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL")

if not FIREBASE_DATABASE_URL:
    raise Exception("Firebase database URL not found in .env file")

# Initialize Firebase
firebase_app = firebase.FirebaseApplication(FIREBASE_DATABASE_URL, None)

class FirebaseMessage(TypedDict):
  isSentByBot: bool
  text: str
  sentAt: str # ISO 8601
  id: Union[str, int]

def email_to_key(email: str):
    return email.replace('.', '_')

def save_token(user_id, token):
    result = firebase_app.put(f'/userTokens/{user_id}', 'token', token)
    return result

def get_token(user_id):
    result = firebase_app.get(f'/userTokens/{user_id}', 'token')
    return result or {}

def write_chat_message(user_email: str, message: str, callback_str: Optional[str]):
    id = str(uuid.uuid4())
    message: FirebaseMessage = {
        "id": id,
        "text": message,
        "isSentByBot": True,
        "sentAt": datetime.now(tz=pytz.timezone("America/New_York")).isoformat(),
        "callback": callback_str
    }
    result = firebase_app.post(f"/chats/{user_email}", message)
    return result is not None
