from celeryy import app as celery_app
from datetime import date
from .models import Notification
from django.utils.timezone import now, timedelta
from .models import Client, Etude, Student, Message


@celery_app.task
def send_reminder_emails():
    today = date.today()
    notifications = Notification.objects.filter(date_effet=today)
    for notif in notifications:
        notif.send()

#------------------------------------------------------------
#(ADLE): called in views.annuaire to refactore the code
def fetch_clients(je_id):
    return list(Client.objects.filter(je=je_id))


def fetch_students(je_id):
    return list(Student.objects.filter(je=je_id))


def fetch_etudes(je_id):
    return list(Etude.objects.filter(je=je_id))


def fetch_messages(user_id):
    return list(
        Message.objects.filter(
            destinataire_id=user_id,
            read=False,
            date__range=(now() - timedelta(days=20), now()),
        )
        .order_by("date")[:3]
        .values()
    )


def fetch_notifications(user):
    return user.notifications.order_by("-date_effet")


