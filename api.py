from datetime import datetime, timedelta, date
from fastapi import FastAPI, Request, Response
from fastapi.logger import logger
from starlette.middleware.sessions import SessionMiddleware
import os
from json import dumps, loads
import google_auth_oauthlib.flow
from constants import BASE_URL, GOOGLE_SCOPES
import logging
from typing import List, TypedDict, Union
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts.chat import ChatPromptTemplate
from google_cal import GoogleCalendarEvent, add_calendar_event, get_calendar_events
import db


# Ensure that all requests include an 'example.com' or
# '*.example.com' host header, and strictly enforce https-only access.
# middleware = [
#     # Middleware(
#     #     TrustedHostMiddleware,
#     #     allowed_hosts=['example.com', '*.example.com'],
#     # ),
#     # Middleware(HTTPSRedirectMiddleware),
#     Middleware(SessionMiddleware(secret_key=environ.get('GOOGLE_CLIENT_SECRET')))
# ]

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY not found in .env file")

chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY)
app = FastAPI()
app.add_middleware(SessionMiddleware,
                   secret_key=os.environ.get("GOOGLE_CLIENT_SECRET"))


@app.on_event("startup")
async def startup_event():
    global logger
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.get("/users/")
async def get_users():
    return db.get_users()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return db.get_user(user_id)


@app.put("/users")
async def add_user(
    username: str,
    name: str,
    email: str,
    google_refresh_token: str,
):
    return db.add_user(username, name, email, google_refresh_token)


@app.patch("/users/{user_id}")
async def edit_user(
    user_id: int,
    username: str,
    name: str,
    email: str,
    google_refresh_token: str,
):
    print("success")
    return db.edit_user(user_id, username, name, email, google_refresh_token)


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    return db.delete_user(user_id)


@app.get("/tasks/")
async def get_tasks():
    return db.get_tasks()


@app.get("/tasks/{user_id}")
async def get_tasks_from_user(user_id: int):
    return db.get_tasks_from_user(user_id)


@app.put("/tasks")
async def add_task(user_id: int, name: str, description: str = "", recurring: bool = False):
    return db.add_task(user_id, name, description, recurring)


@app.patch("/tasks/{task_id}")
async def edit_task(task_id: int, name: str, description: str = ""):
    return db.edit_task(task_id, name, description)


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    return db.delete_task(task_id)


@app.get("/google_oauth_callback")
async def google_oauth_callback(request: Request, response: Response):
    state, username, telegram_user_id = None, None, None
    if "state" in request.query_params:
        state_dict_dumps = request.query_params.get("state")
        if not state_dict_dumps:
            raise Exception("state not in session")
        state_dict = json.loads(state_dict_dumps)
        telegram_user_id = state_dict["telegram_user_id"]
        username = state_dict["username"]
    else:
        raise Exception("state not in session")
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config={
            "web": {
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "project_id": "nova-401105",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": ["http://127.0.0.1:8000/google_oauth_callback"],
                "javascript_origins": ["http://localhost:8000"],
            }
        },
        scopes=GOOGLE_SCOPES,
        state=state,
    )
    flow.redirect_uri = BASE_URL + "/google_oauth_callback"
    code = request.query_params.get("code")

    flow.fetch_token(code=code)

    logger.info("flow.credentials: " + str(flow.credentials))

    # Store the credentials in the session.
    credentials = flow.credentials
    request.session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        # 'token_uri': credentials.token_uri,
        "scopes": credentials.scopes,
    }

    data = {
        "username": username or "bad_entry",
        "name": "",
        "email": "",
        "google_refresh_token": flow.credentials.refresh_token,
    }
    supabase.table("Users").insert(data).execute()
    

    # Create a Response object with the 307 redirect status code
    response = Response(
        status_code=307, headers={"Location": "https://www.t.me/brio_tracker_bot"}
    )

    # Send the Response object
    return response


def time_slot_to_datetime(time_slot):
    # Create a datetime object for tomorrow's date
    tomorrow = date.today() + timedelta(days=1)

    # Extract the start time and end time from the time_slot string
    start_time_str, end_time_str = time_slot.split(" - ")

    # Convert the start time and end time strings to datetime.time objects
    start_time = datetime.strptime(start_time_str, "%I:%M%p").time()
    end_time = datetime.strptime(end_time_str, "%I:%M%p").time()

    # Combine the date object and the time objects to create datetime.datetime objects
    start_datetime = datetime.combine(tomorrow, start_time)
    end_datetime = datetime.combine(tomorrow, end_time)

    return start_datetime, end_datetime


def generate_schedule_from_hobby(hobby, number_of_sessions):
    # Improve the templates in the future -- not mvp
    template = (
        "You are a helpful personal secretary that helps to schedule daily tasks."
    )
    human_template = "I want to learn {hobby}, help me schedule {number_of_sessions} sessions for the week."
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", template),
            ("human", human_template),
        ]
    )
    chain = chat_prompt | chat_model
    return chain.invoke(
        {"hobby": hobby, "number_of_sessions": number_of_sessions}
    ).content


@app.post("/plan_tasks/{user_id}")
def plan_tasks(user_id: int):
    user = get_user(user_id)
    refresh_token = user.get("google_refresh_token", "")
    # Get events from tomorrow 12am to tomorrow 11:59pm
    today = datetime.utcnow()
    today_midnight = datetime(today.year, today.month, today.day, 0, 0)
    events = get_calendar_events(
        refresh_token=refresh_token,
        timeMin=today_midnight.isoformat() + "Z",
        timeMax=(today_midnight + timedelta(days=1)).isoformat() + "Z",
        k=20,
    )

    formatted_events = [
        {
            "start_time": datetime.fromisoformat(event["start"]["dateTime"]).strftime(
                "%I:%M%p"
            ),
            "end_time": datetime.fromisoformat(
                event.get("end")["dateTime"]
                if not event.get("endTimeUnspecified", False)
                else datetime.utcnow().isoformat()
            ).strftime("%I:%M%p"),
            "description": event.get("summary", ""),
            "id": event["id"],
        }
        for event in events
    ]

    formatted_events_str = dumps(formatted_events)
    print("formatted_events_str", formatted_events_str)

    template = (
        "You are a helpful personal secretary that helps to schedule daily tasks."
    )
    tasks = fetch_tasks_formatted(user_id)
    print(tasks)
    if not tasks:
        return None
    human_template = "This is my schedule for tomorrow (which cannot be changed): \n{formatted_events_str}\nThese are extra tasks I want to do tomorrow, with the lowest id as the most important:\n{tasks}\nHelp me add to my schedule with as many of these tasks as possible. Give a reasonable estimate and you do not have to add all if there is no time. Do NOT create new tasks. Do not return the events or tasks in my existing schedule. Return it in parsable JSON format that can be immediately parsed. The return value should contain id, task name and time slot and nothing else, no other sentences ONLY."
    # It returns in this format:
    # {
    #     "tasks": [
    #         {
    #         "id": 1,
    #         "task_name": "run",
    #         "time_slot": "6:00 AM - 7:00 AM"
    #         },
    #         {
    #         "id": 2,
    #         "task_name": "eat",
    #         "time_slot": "7:30 AM - 8:00 AM"
    #         },
    #         {
    #         "id": 3,
    #         "task_name": "gym",
    #         "time_slot": "8:30 AM - 9:30 AM"
    #         },
    #         {
    #         "id": 4,
    #         "task_name": "school",
    #         "time_slot": "10:00 AM - 4:00 PM"
    #         }
    #     ]
    # }
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", template),
            ("human", human_template),
        ]
    )
    chain = chat_prompt | chat_model
    res = chain.invoke(
        {"formatted_events_str": formatted_events_str, "tasks": tasks}
    ).content
    print("AI RESPONSE", res)
    resParsed: dict = loads(res)
    print("AI RESPONSE PARSED", resParsed)
    tasks = (
        resParsed["tasks"]
        if "tasks" in resParsed
        else (
            resParsed["events"]
            if "events" in resParsed
            else resParsed[[k for k in resParsed][0]]  # Take the first key
        )
    )

    if tasks:
        # add to calendar
        for task in tasks:
            task_desc = task.get(
                "task", task.get("description", task.get("task_name", ""))
            )
            print(f"Adding {task_desc} to calendar")
            # Split the time_slot into start and end times
            time_slot = task["time_slot"]
            start_time, end_time = time_slot_to_datetime(time_slot=time_slot)
            add_calendar_event(
                refresh_token=refresh_token,
                start_time=start_time,
                end_time=end_time,
                summary=task_desc,
            )
        # for loop to mark tasks as added
        for task in tasks:
            mark_task_as_added(task["id"])
            print(f"Marked added {task['id']}")


def fetch_tasks_formatted(user_id: int):
    tasks_json = get_tasks(user_id)
    tasks = ""
    for task in tasks_json:
        tasks += str(task["id"]) + ": " + task["name"] + "\n"
    return tasks
