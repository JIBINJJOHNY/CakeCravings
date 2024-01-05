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
    street_address1 = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='Street Address 1',
        help_text='Format: not required'
    )
    street_address2 = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='Street Address 2',
        help_text='Format: not required'
    )
    town_or_city = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name='Town or City',
        help_text='Format: not required'
    )
    state = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='State',
        help_text='Format: not required'
    )
    country = CountryField(
        blank_label='Country *',
        null=True,
        blank=True,
        default='DE',  # Set Germany as the default country
        verbose_name='Country',
        help_text='Format: not required'
    )
    postcode = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Postcode',
        help_text='Format: not required'
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        unique=True,  # Added uniqueness
        verbose_name='Phone Number',
        help_text='Format: not required, unique=True'
    )
    county = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='County',
        help_text='Format: not required'
    )

    # New field to indicate the primary address
    is_primary_address = models.BooleanField(
        default=False,
        verbose_name='Is Primary Address',
        help_text='Check this if it is the primary address.'
    )

    # Additional fields for user registration
    email_verified = models.BooleanField(
        default=False,
        verbose_name='Email Verified',
        help_text='Indicates whether the user has verified their email.'
    )

    # New field for user roles
    ROLES = (
        ('customer', 'Customer'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLES,
        default='customer',
        verbose_name='Role',
        help_text='User role in the system.'
    )

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


# Signal to create a profile when a new user is registered
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# Signal to save the profile when the user is saved
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
