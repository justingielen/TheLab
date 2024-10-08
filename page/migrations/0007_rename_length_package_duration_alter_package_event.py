# Generated by Django 5.0 on 2024-08-27 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0006_package_length_package_number_of_sessions_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='package',
            old_name='length',
            new_name='duration',
        ),
        migrations.AlterField(
            model_name='package',
            name='event',
            field=models.CharField(choices=[('p(r)ep_talk', 'P(r)ep Talk'), ('private_training', 'Private Training'), ('clinic', 'Clinic')], max_length=20),
        ),
    ]
