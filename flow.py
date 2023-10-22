from datetime import datetime
from FirebaseService import write_chat_message
from ai import adjusting_existing_schedule_prompt, storing_new_input_prompt
from db import get_task, get_user, edit_task
from google_cal import add_calendar_event, get_calendar_events


def reply_flow(todo_id: int, message: str):
    todo = get_task(todo_id)
    todo_type = todo["type"]
    todo_state = todo["state"]
    if todo_type == "tasks":
        if todo_state == "missing_deadline":
            datetime_format = "%Y-%m-%d %H:%M:%S"
            datetime_object = datetime.strptime(message, datetime_format)
            edit_task(task_id=todo_id, deadline=datetime_object)
        elif todo_state == "missing_duration":
            edit_task(task_id=todo_id, estimated_duration=int(message))
    elif todo_type == "events":
        if todo_state == "missing_event_start":
            datetime_format = "%Y-%m-%d %H:%M:%S"
            datetime_object = datetime.strptime(message, datetime_format)
            edit_task(task_id=todo_id, event_start=datetime_object)
        elif todo_state == "missing_event_end":
            datetime_format = "%Y-%m-%d %H:%M:%S"
            datetime_object = datetime.strptime(message, datetime_format)
            edit_task(task_id=todo_id, event_end=datetime_object)
    elif todo_type == "habits":
        if todo_state == "missing_duration":
            edit_task(task_id=todo_id, estimated_duration=int(message))
        elif todo_state == "missing_frequency":
            edit_task(task_id=todo_id, frequency=int(message))

    if todo_state == "adjusting":
        if (message.lower() == "ok"):
            # add to calender here
            refresh_token = get_user(todo["user_id"])["google_refresh_token"]
            add_calendar_event(
                todo, refresh_token, todo["name"], todo["description"], todo["adjusted_start"], todo["adjusted_end"])
            edit_task(task_id=todo.id, state="added_to_calendar")
        else:
            # please dont come here
            print("wrong input")

    update_state(todo)


def update_state(todo):
    if todo.state != "adjusting":
        if todo.type == "tasks":
            if todo.deadline == None:
                edit_task(task_id=todo.id, state="missing_deadline")
                message = f"When is {todo.name} due?"
                write_chat_message(get_user(todo["user_id"])[
                                   "email"], message, f"/reply/{todo.id}")
                return
            elif todo.estimated_duration == None:
                edit_task(task_id=todo.id, state="missing_duration")
                message = f"What is the estimated duration for {todo.name}?"
                write_chat_message(get_user(todo["user_id"])[
                                   "email"], message, f"/reply/{todo.id}")
                return

        elif todo.type == "events":
            if todo.event_start == None:
                edit_task(task_id=todo.id, state="missing_event_start")
                message = "When does the event start?"
                write_chat_message(get_user(todo["user_id"])[
                                   "email"], message, f"/reply/{todo.id}")
                return
            elif todo.event_end == None:
                edit_task(task_id=todo.id, state="missing_event_end")
                message = "When does the event end?"
                write_chat_message(get_user(todo["user_id"])[
                                   "email"], message, f"/reply/{todo.id}")
                return

        elif todo.type == "habits":
            if todo.estimated_duration == None:
                edit_task(task_id=todo.id, state="missing_duration")
                message = f"How long do you estimate it takes to do {todo.name}?"
                write_chat_message(get_user(todo["user_id"])[
                                   "email"], message, f"/reply/{todo.id}")
                return
            elif todo.frequency == None:
                edit_task(task_id=todo.id, state="missing_frequency")
                message = f"How often would you like to do {todo.name}?"
                write_chat_message(get_user(todo["user_id"])[
                                   "email"], message, f"/reply/{todo.id}")
                return

        edit_task(task_id=todo.id, state="adjusting")
        # call the ai here
        refresh_token = get_user(todo["user_id"])["google_refresh_token"]
        time_now = datetime.now(tz=pytz.timezone("America/New_York"))
        midnight = datetime(
            time_now.year, time_now.month, time_now.day, 23, 59, 59
        )
        events = get_calendar_events(
            refresh_token=refresh_token,
            timeMin=time_now.isoformat() + "Z",
            timeMax=midnight.isoformat() + "Z",
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

        todo = {}
        if todo.type == "tasks":
            todo = {
                "type": "Task",
                "name": todo.name,
                "description": todo.description,
                "estimated_duration": todo.estimated_duration,
                "deadline": todo.deadline,
            }
        elif todo.type == "events":
            todo = {
                "type": "Event",
                "name": todo.name,
                "description": todo.description,
                "start_time": todo.event_start,
                "end_time": todo.event_end,
            }
        elif todo.type == "habits":
            todo = {
                "type": "Habit",
                "name": todo.name,
                "description": todo.description,
                "frequency": todo.frequency,
                "estimated_duration": todo.estimated_duration,
            }

        pre_message = f"""
        {todo}

        Today's Schedule Format
        {formatted_events}
        """
        message = adjusting_existing_schedule_prompt(pre_message)
        write_chat_message(get_user(todo["user_id"])[
            "email"], message, f"/reply/{todo.id}")
        resParsed: dict = loads(message)
        edit_task(task_id=todo.id,
                  adjusted_start=resParsed["start_time"], adjusted_end=resParsed["end_time"])


def add_new_task_flow(message: str):
    # call ai prompt 1
    todo_data = storing_new_input_prompt(message)

    # map type to enum
    # map description to name
    # add fields accordingly
    # map start_time to event_start
    # map end_time to event_end
    # if gpt returns "none", convert to none

    resParsed: dict = loads(todo_data)

    name = resParsed["description"]

    if resParsed["type"] == "Task":
        type = "tasks"
        deadline = None if resParsed["deadline"] == "none" else resParsed["deadline"]
        estimated_duration = None if resParsed["estimated_duration"] == "none" else resParsed["estimated_duration"]
        todo = supabase.table("Tasks").insert(
            {"type": type, "name": name, "deadline": deadline, "estimated_duration": estimated_duration}).execute()
    elif resParsed["type"] == "Event":
        type = "events"
        event_start = None if resParsed["start_time"] == "none" else resParsed["start_time"]
        event_end = None if resParsed["end_time"] == "none" else resParsed["end_time"]
        todo = supabase.table("Tasks").insert(
            {"type": type, "name": name, "event_start": event_start, "event_end": event_end}).execute()
    elif resParsed["type"] == "Habit":
        type = "habits"
        frequency = None if resParsed["frequency"] == "none" else resParsed["frequency"]
        estimated_duration = None if resParsed["estimated_duration"] == "none" else resParsed["estimated_duration"]
        todo = supabase.table("Tasks").insert(
            {"type": type, "name": name, "frequency": frequency, "estimated_duration": estimated_duration}).execute()
    update_state(todo)
