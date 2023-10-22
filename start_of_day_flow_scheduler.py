# from datetime import datetime, timedelta
# import pytz
# from google_cal import get_calendar_events
# from db import get_user
# from cloud_scheduler import schedule_message_job
# import time

# user = get_user(17)
# refresh_token = user.get("google_refresh_token", "")
# # Get events from tomorrow 12am to tomorrow 11:59pm
# tomorrow = datetime.now(tz=pytz.timezone(
#     "America/New_York"))
# print(tomorrow)
# tomorrow_midnight = datetime(
#     tomorrow.year, tomorrow.month, tomorrow.day, 0, 0
# )
# print(tomorrow_midnight)
# events = get_calendar_events(
#     refresh_token=refresh_token,
#     timeMin=tomorrow_midnight.isoformat() + "Z",
#     timeMax=(tomorrow_midnight + timedelta(days=1)).isoformat() + "Z",
#     k=20,
# )

# formatted_events = [
#     {
#         "start_time": datetime.fromisoformat(event["start"]["dateTime"]).strftime(
#             "%I:%M%p"
#         ),
#         "end_time": datetime.fromisoformat(
#             event.get("end")["dateTime"]
#             if not event.get("endTimeUnspecified", False)
#             else datetime.utcnow().isoformat()
#         ).strftime("%I:%M%p"),
#         "description": event.get("summary", ""),
#         "id": event["id"],
#     }
#     for event in events
# ]

# formatted_schedule = "\n".join(
#     [f"{i+1}. {item['start_time']} - {item['end_time']}: {item['description']}" for i, item in enumerate(formatted_events)])
# template = f'Good morning! Here is your schedule for today:\n{formatted_schedule}'

# # schedule_message_job(17, template, datetime.now() + timedelta(minutes=1))

# # wait for 1 second
# time.sleep(1)

# check_in_1 = f'It’s time for Hack Harvard Presentation!'
# post_check_1 = f'Have you completed Hack Harvard Presentation?'
# check_in_2 = f'It’s time to Take a nap!'
# post_check_2 = f'Have you completed taking a nap?'
# check_in_3 = f"It’s time for Trader Joe's run!"
# post_check_3 = f'Have you completed Trader Joe’s run?'

# schedule_message_job(17, check_in_1, datetime.now().replace(hour=8, minute=25, second=0, microsecond=0))
# schedule_message_job(17, post_check_1, datetime.now().replace(
#     hour=9, minute=0, second=0, microsecond=0))
# schedule_message_job(17, check_in_2, datetime.now().replace(
#     hour=8, minute=55, second=0, microsecond=0))
# schedule_message_job(17, post_check_2, datetime.now().replace(
#     hour=9, minute=30, second=0, microsecond=0))
# schedule_message_job(17, check_in_3, datetime.now().replace(
#     hour=9, minute=25, second=0, microsecond=0))
# schedule_message_job(17, post_check_3, datetime.now().replace(
#     hour=10, minute=0, second=0, microsecond=0))
