# Generated by Django 5.0.2 on 2024-03-03 11:24

import django.db.models.deletion
from django.db import migrations, models
from polls.models import JE


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_alter_client_je_alter_etude_frais_dossier_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='phase',
            name='numero',
            field=models.IntegerField(default=1),
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
        migrations.CreateModel(
            name='AssignationJEH',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pourcentage_retribution', models.FloatField()),
                ('nombre_JEH', models.IntegerField()),
                ('eleve', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='polls.student')),
                ('phase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.phase')),
            ],
        ),
    ]