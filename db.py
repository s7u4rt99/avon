from datetime import datetime
from json import loads
import os
from dotenv import load_dotenv
from supabase.client import create_client

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

if not API_URL or not API_KEY:
    raise Exception("API_URL or API_KEY not found in .env file")

supabase = create_client(API_URL, API_KEY)


def get_users():
    return supabase.table("Users").select("*").execute().data


def get_user(user_id: int):
    return supabase.table("Users").select("*").eq("id", user_id).execute().data[0]


def get_user_by_email(email: str):
    users = supabase.table("Users").select("*").eq("email", email).execute().data
    if len(users) == 0:
        return None
    else:
        return users[0]


def add_user(
    username: str = "",
    name: str = "",
    email: str = "",
    google_refresh_token: str = "",
    terra_user_id: str = " ",
):
    return (
        supabase.table("Users")
        .insert(
            {
                "username": username,
                "name": name,
                "email": email,
                "google_refresh_token": google_refresh_token,
                "terra_user_id": terra_user_id,
            }
        )
        .execute()
    )


def edit_user(
    user_id: int,
    username: str = "",
    name: str = "",
    email: str = "",
    google_refresh_token: str = "",
    terra_user_id: str = "",
):
    data = {}

    if username != "":
        data["username"] = username

    if name != "":
        data["name"] = name

    if email != "":
        data["email"] = email

    if terra_user_id != "":
        data["terra_user_id"] = terra_user_id

    if google_refresh_token != "":
        data["google_refresh_token"] = google_refresh_token

    return supabase.table("Users").update(data).eq("id", user_id).execute()


def delete_user(user_id: int):
    return supabase.table("Users").delete().eq("id", user_id).execute()


def get_tasks():
    return supabase.table("Tasks").select("*").execute().data


def get_task(todo_id: int):
    return supabase.table("Tasks").select("*").eq("id", todo_id).execute().data[0]


def get_tasks_from_user(user_id: int):
    return (
        supabase.table("Tasks")
        .select("*")
        .eq("user_id", user_id)
        .eq("added", False)
        .execute()
        .data
    )

def get_tasks_from_user_email(email: str):
    return (
        supabase.table("Tasks")
        .select("*")
        .eq("email", email)
        .execute()
        .data
    )


def add_task(user_id: int, name: str, description: str = "", recurring: bool = False):
    return (
        supabase.table("Tasks")
        .insert(
            {
                "user_id": user_id,
                "name": name,
                "description": description,
                "recurring": recurring,
            }
        )
        .execute()
    )


def edit_task(
    task_id: int,
    name: str,
    description: str = "",
    deadline: datetime = None,
    estimated_duration: int = None,
    frequency: int = None,
    state: str = None,
    event_start: datetime = None,
    event_end: datetime = None,
    adjusted_start: datetime = None,
    adjusted_end: datetime = None,
):
    data = {}

    if name != "":
        data["name"] = name

    if description != "":
        data["description"] = description

    if deadline != None:
        data["deadline"] = deadline

    if estimated_duration != None:
        data["estimated_duration"] = estimated_duration

    if frequency != None:
        data["frequency"] = frequency

    if state != None:
        data["state"] = state

    if event_start != None:
        data["event_start"] = event_start

    if event_end != None:
        data["event_end"] = event_end

    if adjusted_start != None:
        data["adjusted_start"] = adjusted_start

    if adjusted_end != None:
        data["adjusted_end"] = adjusted_end

    return supabase.table("Tasks").update(data).eq("id", task_id).execute()


def delete_task(task_id: int):
    return supabase.table("Tasks").delete().eq("id", task_id).execute()


def mark_task_as_added(task_id):
    return supabase.table("Tasks").update({"added": True}).eq("id", task_id).execute()


def fetch_tasks_formatted(user_id: int):
    tasks_json = get_tasks_from_user(user_id)
    tasks = ""
    for task in tasks_json:
        tasks += str(task["id"]) + ": " + task["name"] + "\n"
    return tasks


# for testing purposes only
def message(user_id: int, message: str):
    return (supabase.table("MessageTest").insert({"user_id": user_id, "message": message}).execute())
