from fastapi import FastAPI, Request, Response
from fastapi.logger import logger
from starlette.middleware.sessions import SessionMiddleware
import os
import json
import google_auth_oauthlib.flow
# from constants import BASE_URL, GOOGLE_SCOPES
# from database import add_user
import logging
from typing import List, TypedDict, Union
from dotenv import load_dotenv
from supabase.client import create_client

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

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

if not API_URL or not API_KEY:
    raise Exception("API_URL or API_KEY not found in .env file")

supabase = create_client(API_URL, API_KEY)


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
    return (
        supabase.table("Users")
        .select("*")
        .execute()
        .data
    )


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return (
        supabase.table("Users")
        .select("*")
        .eq("id", user_id)
        .execute()
        .data
    )


@app.put("/users")
async def add_user(
    username: str,
    name: str,
    email: str,
    google_refresh_token: str,
):
    return (
        supabase.table("Users")
        .insert(
            {
                "username": username,
                "name": name,
                "email": email,
                "google_refresh_token": google_refresh_token,
            }
        )
        .execute()
    )


@app.patch("/users/{user_id}")
async def edit_user(
    user_id: int,
    username: str,
    name: str,
    email: str,
    google_refresh_token: str,
):

    data = {}

    if username is not "":
        data["username"] = username

    if name is not "":
        data["name"] = name

    if email is not "":
        data["email"] = email

    if google_refresh_token is not "":
        data["google_refresh_token"] = google_refresh_token

    return (
        supabase.table("Users")
        .update(data)
        .eq("id", user_id)
        .execute()
    )


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    return (
        supabase.table("Users")
        .delete()
        .eq("id", user_id)
        .execute()
    )


@app.get("/tasks/")
async def get_tasks():
    return (
        supabase.table("Tasks")
        .select("*")
        .execute()
        .data
    )


@app.get("/tasks/{user_id}")
async def get_tasks_from_user(user_id: int):
    return (
        supabase.table("Tasks")
        .select("*")
        .eq("id", user_id)
        .eq("added", False)
        .execute()
        .data
    )


@app.put("/tasks")
async def add_task(user_id: int, name: str, description: str = "", recurring: bool = False):
    return (
        supabase.table("Tasks")
        .insert({"user_id": user_id,
                 "name": name,
                 "description": description,
                 "recurring": recurring})
        .execute()
    )


@app.patch("/tasks/{task_id}")
async def edit_task(task_id: int, name: str, description: str = ""):
    data = {}

    if name is not "":
        data["name"] = name

    if description is not "":
        data["description"] = description

    return (
        supabase.table("Tasks")
        .update(data)
        .eq("id", task_id)
        .execute()
    )


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    return (
        supabase.table("Tasks")
        .delete()
        .eq("id", task_id)
        .execute()
    )


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
