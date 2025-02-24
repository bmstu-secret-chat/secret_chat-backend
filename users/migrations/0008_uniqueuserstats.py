# Generated by Django 5.1.2 on 2025-02-23 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_is_online_user_last_online'),
    ]

    operations = [
        migrations.CreateModel(
            name='UniqueUserStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('daily_users', models.IntegerField(default=0)),
                ('monthly_users', models.IntegerField(default=0)),
            ],
        ),
    ]
