# Generated by Django 4.2.7 on 2024-01-11 11:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, help_text='Format: not required, max_length=50', max_length=50, null=True, verbose_name='First name')),
                ('last_name', models.CharField(blank=True, help_text='Format: not required, max_length=50', max_length=50, null=True, verbose_name='Last name')),
                ('birthday', models.DateField(blank=True, help_text='Format: not required', null=True, verbose_name='Birthday')),
                ('street_address1', models.CharField(blank=True, help_text='Format: not required', max_length=80, null=True, verbose_name='Street Address 1')),
                ('street_address2', models.CharField(blank=True, help_text='Format: not required', max_length=80, null=True, verbose_name='Street Address 2')),
                ('town_or_city', models.CharField(blank=True, help_text='Format: not required', max_length=40, null=True, verbose_name='Town or City')),
                ('state', models.CharField(blank=True, choices=[('BW', 'Baden-Württemberg'), ('BY', 'Bavaria (Bayern)'), ('BE', 'Berlin'), ('BB', 'Brandenburg'), ('HB', 'Bremen'), ('HH', 'Hamburg'), ('HE', 'Hesse (Hessen)'), ('NI', 'Lower Saxony (Niedersachsen)'), ('MV', 'Mecklenburg-Western Pomerania (Mecklenburg-Vorpommern)'), ('NW', 'North Rhine-Westphalia (Nordrhein-Westfalen)'), ('RP', 'Rhineland-Palatinate (Rheinland-Pfalz)'), ('SL', 'Saarland'), ('SN', 'Saxony (Sachsen)'), ('ST', 'Saxony-Anhalt (Sachsen-Anhalt)'), ('SH', 'Schleswig-Holstein'), ('TH', 'Thuringia (Thüringen)')], help_text='German state', max_length=2, null=True, verbose_name='State')),
                ('country', django_countries.fields.CountryField(blank=True, default='DE', help_text='Format: not required', max_length=2, null=True, verbose_name='Country')),
                ('postcode', models.CharField(blank=True, help_text='Format: not required', max_length=20, null=True, verbose_name='Postcode')),
                ('phone_number', models.CharField(blank=True, help_text='Format: not required, unique=True', max_length=20, null=True, unique=True, verbose_name='Phone Number')),
                ('county', models.CharField(blank=True, help_text='Format: not required', max_length=80, null=True, verbose_name='County')),
                ('is_primary_address', models.BooleanField(default=False, help_text='Check this if it is the primary address.', verbose_name='Is Primary Address')),
                ('email_verified', models.BooleanField(default=False, help_text='Indicates whether the user has verified their email.', verbose_name='Email Verified')),
                ('role', models.CharField(choices=[('customer', 'Customer'), ('manager', 'Manager'), ('admin', 'Admin')], default='customer', help_text='User role in the system.', max_length=10, verbose_name='Role')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('user', models.OneToOneField(help_text='Format: required, unique=True', on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]
