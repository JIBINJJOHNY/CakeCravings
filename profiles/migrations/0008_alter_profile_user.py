# Generated by Django 4.2.7 on 2024-01-03 22:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profiles', '0007_alter_profile_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(help_text='Format: required, unique=True', on_delete=django.db.models.deletion.CASCADE, related_name='profile_set', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
