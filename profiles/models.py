from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django_countries.fields import CountryField
from datetime import date

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='User',
        help_text='Format: required, unique=True'
    )
    first_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='First name',
        help_text='Format: not required, max_length=50'
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Last name',
        help_text='Format: not required, max_length=50'
    )
    birthday = models.DateField(
        blank=True,
        null=True,
        verbose_name='Birthday',
        help_text='Format: not required'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
    )
    subscription = models.BooleanField(
        default=False,
        verbose_name='Subscription',
        help_text='Format: not required'
    )

    default_phone_number = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label='Country *', null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at',
    )

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        if self.first_name:
            return self.first_name
        return self.user.username

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default_avatar.svg'

    @property
    def age(self):
        if self.birthday:
            today = date.today()
            birthday = (
                today.year -
                self.birthday.year -
                (
                    (today.month, today.day) < (
                        self.birthday.month, self.birthday.day
                    )
                )
            )
            if birthday < 0:
                return 'Invalid birthday'
            return birthday
        return None

