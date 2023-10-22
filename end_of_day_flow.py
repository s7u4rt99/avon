from datetime import datetime, timedelta
from json import loads
from typing import List
import pytz
from ai import night_new_schedule_prompt
from db import get_tasks_from_user_email, get_user_by_email
from google_cal import GoogleCalendarEvent, get_calendar_events, get_readable_cal_event_string

def generate_event_summary(refresh_token: str):
  """
  Get the summary of all things done in google cal today
  """
  current_time = datetime.now(tz=pytz.timezone("America/New_York"))
  today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
  today_end = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)

  # Get all events from today
  events = get_calendar_events(refresh_token=refresh_token, timeMin=today_start.isoformat() + "Z", timeMax=today_end.isoformat() +"Z", k = 50)
  events_str = get_readable_cal_event_string(events)
  return events_str

def generate_health_summary():
  """
  Get the summary of all things done in health APIs today

  TODO: Implement Terra and Finish this
  """
  return ""

def generate_all_summary(email: str):
  """
  Get the summary of all things done today
  """
  user = get_user_by_email(email=email)
  if user is None:
    return
  else:
    events_str = generate_event_summary(refresh_token=user.get("google_refresh_token", ""))
    health_str = generate_health_summary()

    return f"""As the day winds down, here's a summary of what you've done today:
{events_str}

{health_str and f"and not to forget, your fitness updates: {health_str}"}

Great Job!
"""
  
def get_tomorrow_events(email: str) -> List[GoogleCalendarEvent]:
  """
  Get the schedule for tomorrow
  """
  user = get_user_by_email(email=email)

  curr_time = datetime.now(tz=pytz.timezone("America/New_York"))
  tomorrow = curr_time + timedelta(days=1)
  tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
  tomorrow_end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)

  # Get all events from tomorrow
  events = get_calendar_events(refresh_token=user.get("refresh_token", ""), timeMin=tomorrow_start.isoformat() + "Z", timeMax=tomorrow_end.isoformat() +"Z", k = 50)
  return events
  
def start_night_flow(email: str):
  """
  Start the night flow.
  1. Generate day's summary
  2. Get tomorrow's schedule
  3. Try to add unfinished tasks to schedule and add to calendar
  4. Tell user what's been added and direct to google calendar
  """

  # 1. Generate day's summary
  summary = generate_all_summary(email=email)

  # 2. Get tomorrow's schedule
  tomorrow_events = get_tomorrow_events(email=email)
  tomorrow_events_str = get_readable_cal_event_string(tomorrow_events)

  # 3. Try to add unfinished tasks to schedule and add to calendar
  task_list = get_tasks_from_user_email(email=email)
  unfinished_tasks = [task for task in task_list if (task.get("completed", False) == False) and (task.get("type", "task") == "task")]
  habit_goals = [task for task in task_list if (task.get("completed", False) == False) and (task.get("type", "task") == "habit")]
  new_schedule = night_new_schedule_prompt(
    f"""
    Uncompleted Tasks:
    {unfinished_tasks}

    Existing Events on Calendar:
    {tomorrow_events_str}

    Habits to do:
    {habit_goals}
    """                    
  )

  schedule_obj = loads(new_schedule)

