import os
import pytz
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from json import dumps, loads
from db import fetch_tasks_formatted, get_user, mark_task_as_added
from google_cal import get_calendar_events
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts.chat import ChatPromptTemplate
from google_cal import GoogleCalendarEvent, add_calendar_event, get_calendar_events

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY not found in .env file")

chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY)


def time_slot_to_datetime(time_slot):
    # Create a datetime object for tomorrow's date
    tomorrow = date.today() + timedelta(days=1)

    # Extract the start time and end time from the time_slot string
    start_time_str, end_time_str = time_slot.split(" - ")

    # Convert the start time and end time strings to datetime.time objects
    if len(start_time_str) == 6:
        start_time_str = "0" + start_time_str

    if len(end_time_str) == 6:
        end_time_str = "0" + end_time_str

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


def plan_tasks(user_id: int):
    user = get_user(user_id)
    refresh_token = user.get("google_refresh_token", "")
    # Get events from tomorrow 12am to tomorrow 11:59pm
    tomorrow = datetime.now(tz=pytz.timezone("America/New_York")) + timedelta(days=1)
    print(tomorrow)
    tomorrow_midnight = datetime(
        tomorrow.year, tomorrow.month, tomorrow.day, 0, 0
    )
    print(tomorrow_midnight)
    events = get_calendar_events(
        refresh_token=refresh_token,
        timeMin=tomorrow_midnight.isoformat() + "Z",
        timeMax=(tomorrow_midnight + timedelta(days=1)).isoformat() + "Z",
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

    print("events", events)
    formatted_events_str = dumps(formatted_events)
    print("formatted_events_str", formatted_events_str)

    template = (
        "You are a helpful personal secretary that helps to schedule daily tasks."
    )
    tasks = fetch_tasks_formatted(user_id)
    print(tasks)
    if not tasks:
        return None
    human_template = "This is my schedule for tomorrow (which cannot be changed): \n{formatted_events_str}\nThese are extra tasks I want to do tomorrow, with the lowest id as the most important:\n{tasks}\nHelp me add to my schedule with as many of these tasks as possible. Give a reasonable estimate and you do not have to add all if there is no time. Do NOT create new tasks. Do not return the events or tasks in my existing schedule. Return it in parsable JSON format that can be immediately parsed. The return json should have keys id, task_name and time_slot and nothing else, no other sentences ONLY."
    # It returns in this format:
    # {
    #     "tasks": [
    #         {
    #         "id": 1,
    #         "task_name": "run",
    #         "time_slot": "06:00 AM - 7:00 AM"
    #         },
    #         {
    #         "id": 2,
    #         "task_name": "eat",
    #         "time_slot": "07:30 AM - 8:00 AM"
    #         },
    #         {
    #         "id": 3,
    #         "task_name": "gym",
    #         "time_slot": "08:30 AM - 9:30 AM"
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

    return tasks


def storing_new_input_prompt(user_input: str):
    template = (
        """
        You're the productivity copilot, tasked with taking note of the user's tasks/events/habits and organizing the user's day in a JSON format.

        You have already come up with the user's schedule for today the previous night. However, the user just sent a new input.

        Sort new inputs as "Event", "Task", or "Habit".

        For New Events: Return a JSON object with the following structure:
        
        {{
        "type": "Event",
        "command": "/event",
        "description": "<event description>",
        "start_time": "<start time>",
        "end_time": "<end time>"
        }}

        For New Tasks: Return a JSON object with the following structure:

        {{
        "type": "Task",
        "command": "/task",
        "description": "<task description>",
        "deadline": "<deadline>",
        "estimated_duration": "<estimated duration>"
        }}

        For New Habits: Return a JSON object with the following structure:

        {{
        "type": "Habit",
        "command": "/habit",
        "description": "<habit description>",
        "frequency": "<frequency>",
        "estimated_duration": "<estimated duration>"
        }}

        If the user didn't provide any of the required info, represent it with "none".
        """
    )

    human_template = "{user_input}"

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", template),
            ("human", human_template),
        ]
    )
    chain = chat_prompt | chat_model
    res = chain.invoke({"user_input": user_input}).content
    print("AI RESPONSE", res)


def adjusting_existing_schedule_prompt(user_input: str):
    template = (
        """
        You are the Productivity Co-Pilot, in charge of fine-tuning the user's schedule based on incoming events, tasks, and habits. You've crafted today's schedule, but the user has just sent a new task requiring adjustments.

        Input Formats

        For New Task:  
        {{
        "type": "Task",
        "command": "/task",
        "description": "<task description>",
        "deadline": "<deadline>",
        "estimated_duration": "<estimated duration>"
        }}

        For New Habit:
        {{
        "type": "Habit",
        "command": "/habit",
        "description": "<habit description>",
        "frequency": "<frequency>",
        "estimated_duration": "<estimated duration>"
        }}

        For New Event: 
        {{
        "type": "Event",
        "command": "/event",
        "description": "<event description>",
        "start_time": "<start time>",
        "end_time": "<end time>"
        }}

        Scheduling Rules
        On receiving a new event, seamlessly integrate it into the existing schedule for the day. If a conflict occurs, confirm with the user before reshuffling.
        Prioritize tasks based on their deadlines. If the new task must be completed today, revise the schedule for the day. If not, add it to an "Uncompleted Tasks" list.
        Aim to leave the current schedule unaltered. If unavoidable, reassign tasks or habits rather than meetings or appointments.
        Mandatory 30-minute lunch slot between 12-2pm and a 30-minute dinner slot between 6-8pm.
        Decisions on schedule adjustments should be made autonomously without consulting the user.
        Ensure zero conflicts in the adjusted schedule.

        Today's Schedule Format
        Today's schedule will be in JSON format like so:
        [ {{"start_time": "09:00AM", "end_time": "10:00AM", "description": "Team Meeting", "id": "xyz1"}}, {{"start_time": "11:00AM", "end_time": "12:00PM", "description": "Work on Project X", "id": "xyz2"}}, ... ]

        Response Format
        Your response should be in the following JSON format:

        {{
            "tasks": [
                {{
                "id": 1,
                "task_name": "Team Meeting",
                "time_slot": "09:00 AM - 10:00 AM"
                }},
                ...
            ]
        }}

        Example Scenario
        Today's Schedule:
        [
            {{"start_time": "09:00AM", "end_time": "10:00AM", "description": "Team Meeting", "id": "xyz1"}},
            {{"start_time": "11:00AM", "end_time": "12:00PM", "description": "Work on Project X", "id": "xyz2"}},
            ...
        ]

        New User Input: 
        {{
        "type": "Task",
        "command": "/task",
        "description": "<task description>",
        "deadline": "<deadline>",
        "estimated_duration": "<estimated duration>"
        }}


        Your Response:
        {{ "tasks": [ {{ "id": 1, "task_name": "Submit case study report", "time_slot": "10:30 AM - 01:30 PM" }}, {{ "id": 2, "task_name": "Work on Project X", "time_slot": "01:30 PM - 02:30 PM" }}, {{ "id": 3, "task_name": "Gym", "time_slot": "03:00 PM - 04:30 PM" }} ] }}
        """
    )

    human_template = "{user_input}"

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", template),
            ("human", human_template),
        ]
    )
    chain = chat_prompt | chat_model
    res = chain.invoke({"user_input": user_input}).content
    print("AI RESPONSE", res)


adjusting_existing_schedule_prompt(
    """
    {{
        "type": "Task",
        "command": "/task",
        "description": "get married",
        "deadline": "2026",
        "estimated_duration": "5 hours"
    }}
    """                            
)
