from celeryy import app as celery_app
from datetime import date
from .models import Notification
from celery import shared_task
from django.utils.timezone import now, timedelta
from .models import Client, Etude, Student, Message


@celery_app.task
def send_reminder_emails():
    today = date.today()
    notifications = Notification.objects.filter(date_effet=today)
    for notif in notifications:
        notif.send()


@shared_task
def fetch_clients(je):
    return list(Client.objects.filter(je=je))


@shared_task
def fetch_students(je):
    return list(Student.objects.filter(je=je))


@shared_task
def fetch_etudes(je):
    return list(Etude.objects.filter(je=je))


@shared_task
def fetch_messages(user):
    return list(
        Message.objects.filter(
            destinataire_id=user,
            read=False,
            date__range=(now() - timedelta(days=20), now()),
        )
        .order_by("date")[:3]
        .values()
    )


@shared_task
def fetch_notifications(user):
    return user.notifications.order_by("-date_effet")
