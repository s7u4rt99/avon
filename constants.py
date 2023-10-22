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
    "https://avon-seven.vercel.app"
    if os.getenv("ENVIRONMENT") != "dev"
    else "http://127.0.0.1:8000"
)
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

MORNING_FLOW_TIME = (23, 43)  # (hour, minute)
