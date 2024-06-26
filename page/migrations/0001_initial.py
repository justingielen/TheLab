# Generated by Django 5.0 on 2024-05-21 12:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schedule', '0014_use_autofields_for_pk'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='schedule.event')),
                ('event_type', models.CharField(choices=[('camp', 'Camp'), ('clinic', 'Clinic'), ('training', 'Training')], max_length=255)),
                ('location_notes', models.CharField(blank=True, help_text="(e.g., 'Field 11', or 'Auxiliary Gym')", max_length=255)),
            ],
            bases=('schedule.event',),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_name', models.CharField(max_length=255, unique=True)),
                ('location_type', models.CharField(choices=[('in-person', 'In Person'), ('virtual', 'Virtual')], max_length=20)),
                ('hyperlink', models.CharField(blank=True, max_length=255, null=True)),
                ('street_address', models.CharField(blank=True, max_length=255)),
                ('location_city', models.CharField(blank=True, max_length=255)),
                ('location_state', models.CharField(blank=True, max_length=2)),
                ('location_zip', models.CharField(blank=True, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('occurrence_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='schedule.occurrence')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
            bases=('schedule.occurrence',),
        ),
        migrations.CreateModel(
            name='ProfileSport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Sport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sport', models.CharField(max_length=25, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventSport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='page.event')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.ForeignKey(help_text='(Note: locations must be added to your Profile before they can be used in an Event)', on_delete=django.db.models.deletion.CASCADE, to='page.location'),
        ),
        migrations.CreateModel(
            name='CoachLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='page.location')),
            ],
        ),
        migrations.CreateModel(
            name='PageCalendar',
            fields=[
                ('calendar_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='schedule.calendar')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=('schedule.calendar',),
        ),
    ]
