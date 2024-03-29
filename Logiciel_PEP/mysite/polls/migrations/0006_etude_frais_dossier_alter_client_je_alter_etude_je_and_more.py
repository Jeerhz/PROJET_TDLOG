# Generated by Django 5.0.2 on 2024-02-26 21:11

import django.db.models.deletion
from django.db import migrations, models
from polls.models import JE


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_alter_client_je_alter_etude_je_alter_member_je_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='etude',
            name='frais_dossier',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='client',
            name='je',
            field=models.ForeignKey(default=JE.objects.get(pk='bab6b8bec2744faeb6343c6a40968534'), on_delete=django.db.models.deletion.CASCADE, to='polls.je'),
        ),
        migrations.AlterField(
            model_name='etude',
            name='je',
            field=models.ForeignKey(default=JE.objects.get(pk='bab6b8bec2744faeb6343c6a40968534'), on_delete=django.db.models.deletion.CASCADE, to='polls.je'),
        ),
        migrations.AlterField(
            model_name='member',
            name='je',
            field=models.ForeignKey(default=JE.objects.get(pk='bab6b8bec2744faeb6343c6a40968534'), on_delete=django.db.models.deletion.CASCADE, to='polls.je'),
        ),
        migrations.AlterField(
            model_name='message',
            name='je',
            field=models.ForeignKey(default=JE.objects.get(pk='bab6b8bec2744faeb6343c6a40968534'), on_delete=django.db.models.deletion.CASCADE, to='polls.je'),
        ),
        migrations.AlterField(
            model_name='student',
            name='je',
            field=models.ForeignKey(default=JE.objects.get(pk='bab6b8bec2744faeb6343c6a40968534'), on_delete=django.db.models.deletion.CASCADE, to='polls.je'),
        ),
    ]
