from datetime import datetime, timedelta
from google.cloud import scheduler

client = scheduler.CloudSchedulerClient()

parent = client.common_location_path('avon-402721', 'us-east4')

def schedule_message_job(user_id: int, message: str, time: datetime):
    # convert time to cron expression
    cron_time = f'{time.minute} {time.hour} {time.day} {time.month} *'
    uri = f'https://avon-git-cronjobs-s7u4rt99.vercel.app/message/{user_id}?message={message}'

    # Define the job payload, including the job name, schedule, target HTTP endpoint, and other details
    job = {
        # first 50 characters of message
        'name': f'{parent}/jobs/{user_id}_{message[:50]}_{time.day}-{time.month}-{time.year}_{time.hour}_{time.minute}',
        'http_target': {
            'uri': uri,
            'http_method': 'POST',
        },
        'schedule': cron_time,  # Cron expression for scheduling (e.g., hourly)
        'time_zone': 'America/New_York',  # Timezone to execute the job in
    }

    # Create the job
    response = client.create_job(parent=parent, job=job)
    print(f'Job created: {response.name}')


schedule_message_job(5, 'hello', datetime.now() + timedelta(minutes=1))