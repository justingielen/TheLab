# Generated by Django 5.0.1 on 2024-12-22 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0006_alter_availability_day_alter_package_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availability',
            name='day',
            field=models.CharField(choices=[('Friday', 'Friday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Monday', 'Monday'), ('Sunday', 'Sunday'), ('Saturday', 'Saturday')], max_length=10),
        ),
    ]