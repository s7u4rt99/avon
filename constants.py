import os
from enum import Enum


class Command(str, Enum):
    START = "start"
    HELP = "help"
    ADD = "add"
    TASKS = "tasks"
    SCHEDULE = "schedule"
    CANCEL = "cancel"


BASE_URL = (
    "http://127.0.0.1:8000"
    if os.getenv("ENVIRONMENT") != "prod"
    else "https://avon-seven.vercel.app"
)
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

MORNING_FLOW_TIME = (23, 43)  # (hour, minute)
