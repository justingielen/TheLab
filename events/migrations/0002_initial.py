# Generated by Django 5.0.1 on 2024-12-17 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        ('page', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventattendee',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='page.event'),
        ),
        migrations.AddField(
            model_name='attendeeparent',
            name='attendee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.eventattendee'),
        ),
    ]
