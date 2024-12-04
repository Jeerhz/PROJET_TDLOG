from celeryy import app as celery_app
from datetime import date
from .models import Notification
from django.utils import timezone
from .models import Client, Etude, Student, Message


@celery_app.task
def send_reminder_emails():
    today = date.today()
    notifications = Notification.objects.filter(date_effet=today)
    for notif in notifications:
        notif.send()

#------------------------------------------------------------
#(ADLE): called in views.annuaire to refactore the code
def fetch_clients(user_je_id):
    return list(Client.objects.filter(je=user_je_id))

def fetch_students(user_je_id):
    return list(Student.objects.filter(je=user_je_id))

def fetch_etudes(user_je_id):
    return list(Etude.objects.filter(je=user_je_id))

def fetch_messages(user):
    return list(Message.objects.filter(
        destinataire=user,
        read=False,
        date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now())
    ).order_by("date")[:3])

def fetch_notifications(user):
    return list(user.notifications.order_by("-date_effet"))


