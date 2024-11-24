from celeryy import app as celery_app
from datetime import date
from .models import Notification

@celery_app.task 
def send_reminder_emails():
    today = date.today()
    notifications = Notification.objects.filter(date_effet=today)
    for notif in notifications:
        notif.send()
