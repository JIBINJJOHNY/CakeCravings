from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Signal handler to create a profile when a new user is created."""
    if created:
        # Only create a profile if one doesn't already exist
        Profile.objects.get_or_create(user=instance, defaults={'email_verified': False, 'role': 'customer'})

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    # Check if the user has a profile before saving
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)