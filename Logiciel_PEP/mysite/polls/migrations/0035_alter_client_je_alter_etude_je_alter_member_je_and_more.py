# Generated by Django 4.2.11 on 2024-03-23 13:49

from django.db import migrations, models
import django.db.models.deletion
from polls.models import JE


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0034_alter_client_je_alter_etude_id_url_alter_etude_je_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="je",
            field=models.ForeignKey(
                default=JE.objects.get(pk="bab6b8bec2744faeb6343c6a40968534"),
                on_delete=django.db.models.deletion.CASCADE,
                to="polls.je",
            ),
        ),
        migrations.AlterField(
            model_name="etude",
            name="je",
            field=models.ForeignKey(
                default=JE.objects.get(pk="bab6b8bec2744faeb6343c6a40968534"),
                on_delete=django.db.models.deletion.CASCADE,
                to="polls.je",
            ),
        ),
        migrations.AlterField(
            model_name="member",
            name="je",
            field=models.ForeignKey(
                default=JE.objects.get(pk="bab6b8bec2744faeb6343c6a40968534"),
                on_delete=django.db.models.deletion.CASCADE,
                to="polls.je",
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="je",
            field=models.ForeignKey(
                default=JE.objects.get(pk="bab6b8bec2744faeb6343c6a40968534"),
                on_delete=django.db.models.deletion.CASCADE,
                to="polls.je",
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="je",
            field=models.ForeignKey(
                default=JE.objects.get(pk="bab6b8bec2744faeb6343c6a40968534"),
                on_delete=django.db.models.deletion.CASCADE,
                to="polls.je",
            ),
        ),
    ]