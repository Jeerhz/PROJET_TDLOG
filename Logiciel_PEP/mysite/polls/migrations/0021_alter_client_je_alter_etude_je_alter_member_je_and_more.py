# Generated by Django 5.0.2 on 2024-03-06 17:02

import django.db.models.deletion
from django.db import migrations, models
from polls.models import JE


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0020_alter_client_je_alter_etude_je_alter_member_je_and_more'),
    ]

    operations = [
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