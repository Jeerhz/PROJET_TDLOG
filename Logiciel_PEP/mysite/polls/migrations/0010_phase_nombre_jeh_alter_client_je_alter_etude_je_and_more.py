# Generated by Django 4.2.7 on 2024-02-25 09:51

from django.db import migrations, models
import django.db.models.deletion
from polls.models import JE


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0009_remove_etude_montant_ht_remove_etude_nb_jeh_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="phase",
            name="nombre_JEH",
            field=models.IntegerField(default=300),
            preserve_default=False,
        ),
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