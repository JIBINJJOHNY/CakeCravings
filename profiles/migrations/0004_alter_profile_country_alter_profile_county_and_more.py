# Generated by Django 4.2.7 on 2024-01-02 12:20

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_profile_email_verified_profile_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='country',
            field=django_countries.fields.CountryField(blank=True, help_text='Format: not required', max_length=2, null=True, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='county',
            field=models.CharField(blank=True, help_text='Format: not required', max_length=80, null=True, verbose_name='County'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Format: not required, unique=True', max_length=20, null=True, unique=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='postcode',
            field=models.CharField(blank=True, help_text='Format: not required, unique=True', max_length=20, null=True, unique=True, verbose_name='Postcode'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='street_address1',
            field=models.CharField(blank=True, help_text='Format: not required', max_length=80, null=True, verbose_name='Street Address 1'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='street_address2',
            field=models.CharField(blank=True, help_text='Format: not required', max_length=80, null=True, verbose_name='Street Address 2'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='town_or_city',
            field=models.CharField(blank=True, help_text='Format: not required', max_length=40, null=True, verbose_name='Town or City'),
        ),
    ]
