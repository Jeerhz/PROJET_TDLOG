# Generated by Django 4.2.11 on 2024-03-27 21:05

from django.db import migrations, models
import django.db.models.deletion
from polls.models import JE


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0037_alter_client_je_alter_etude_je_alter_member_je_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="facture", name="fac_JEH", field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="facture", name="fac_frais", field=models.FloatField(default=0),
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
            model_name="facture",
            name="numero_facture",
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name="facture",
            name="pourcentage_JEH",
            field=models.FloatField(default=30),
        ),
        migrations.AlterField(
            model_name="facture",
            name="pourcentage_frais",
            field=models.FloatField(default=30),
        ),
        migrations.AlterField(
            model_name="facture",
            name="type_facture",
            field=models.CharField(
                choices=[
                    ("FAC_ACOMPTE", "facture acompte"),
                    ("FAC_INTER", "facture intermédiare"),
                    ("FAC_SOLDE", "facture de solde"),
                ],
                default="FAC_SOLDE",
                max_length=30,
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