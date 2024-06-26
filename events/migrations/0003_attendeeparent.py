# Generated by Django 5.0 on 2024-06-09 19:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendeeParent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_first_name', models.CharField(default='(first name)', max_length=50)),
                ('parent_last_name', models.CharField(default='(last name)', max_length=50)),
                ('parent_email', models.CharField(max_length=50)),
                ('attendee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.eventattendee')),
            ],
        ),
    ]
