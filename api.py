import requests
import os
import google_auth_oauthlib.flow
import logging
import db
import ai
import json
from fastapi import FastAPI, Request, Response
from fastapi.logger import logger
from starlette.middleware.sessions import SessionMiddleware
from constants import BASE_URL, GOOGLE_SCOPES
from typing import List, TypedDict, Union
from dotenv import load_dotenv
from supabase.client import create_client
from terra.base_client import Terra

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


@app.post("/task/added/{task_id}")
async def mark_task_as_added(task_id: int):
    return db.mark_task_as_added(task_id)


@app.patch("/planTasks/{user_id}")
def plan_tasks(user_id: int):
    return ai.plan_tasks(user_id)


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

TERRA_API_KEY = os.getenv("TERRA_API_KEY")
TERRA_DEV_ID = os.getenv("TERRA_DEV_ID")
TERRA_SIGNING_SECRET = os.getenv("TERRA_SIGNING_SECRET")

if not TERRA_API_KEY or not TERRA_DEV_ID:
    raise Exception("TERRA_API_KEY or TERRA_DEV_ID or TERRA_SIGNING_SECRET not found in .env file")

terra = Terra(api_key=TERRA_API_KEY, dev_id=TERRA_DEV_ID, secret=TERRA_SIGNING_SECRET or "")

@app.post("/generateWidgetSession")
async def generate_widget_session(user_id: int):
    widget_response = terra.generate_widget_session(
        reference_id=user_id,
        providers=["GARMIN"],
        auth_success_redirect_url="https://avon-seven.vercel.app/widgetResponseSuccess",
        auth_failure_redirect_url="https://avon-seven.vercel.app/widgetResponseFailure",
        language="en"
    ).get_parsed_response()

    return {"widget_response": widget_response}


@app.get("/widgetResponseSuccess")
async def handle_widget_response_success(user_id: str, reference_id: str, resource: str):
    db.edit_user(reference_id, terra_user_id=user_id)
    return {"response": "close the browser window"}


@app.get("/widgetResponseFailure")
async def handle_widget_response_failure(user_id: str, resource: str, reference_id: str, lan: str, reason: str):
    # TODO: Handle failure
    db.edit_user(reference_id, terra_user_id=user_id)
    return {"response": "close the browser window"}


@app.get("/listTerraUsers")
async def list_terra_users():
    return {"users": terra.list_users().get_parsed_response()}
    

@app.post("/consumeTerraWebhook")
async def consume_terra_webhook(request: Request):
    body = await request.body()
    body_dict = json.loads(body.decode())
    return {"user": body_dict.get("user", {}).get("user_id"), "type": body_dict["type"], "data": body_dict["data"]}


# for testing purposes only
@app.post("/message/{user_id}")
def message(user_id: int, message: str):
    return db.message(user_id, message)


@app.post("/send_notification/")
async def send_notification(token: str, message: str):
    url = "https://exp.host/--/api/v2/push/send"
    data = {
        "to": token,
        "title": "Your Title",
        "body": message
    }
    response = requests.post(url, json=data)
    return {"status": "Notification sent", "response": response.json()}

