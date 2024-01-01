from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Signal handler to create a profile when a new user is created."""
    if created:
        Profile.objects.create(
            user=instance,
            email_verified=False,  # Default value for email_verified
            role='customer'  # Default value for role
        )

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Signal handler to save the profile when the user is saved."""
    instance.profile.save()
