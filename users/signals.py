from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile when a new User is created
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile when the User is saved
    """
    if hasattr(instance, 'extended_profile'):
        instance.extended_profile.save()


@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    """
    Delete the UserProfile when the User is deleted
    """
    if hasattr(instance, 'extended_profile'):
        instance.extended_profile.delete()


@receiver(post_save, sender=User)
def update_user_kyc_status(sender, instance, **kwargs):
    """
    Update user KYC status when KYC is verified
    """
    if instance.kyc_status == 'verified' and not instance.kyc_verified_at:
        from django.utils import timezone
        instance.kyc_verified_at = timezone.now()
        instance.save(update_fields=['kyc_verified_at'])


@receiver(post_save, sender=User)
def handle_creator_verification(sender, instance, **kwargs):
    """
    Handle creator verification status changes
    """
    if instance.user_type == 'creator' and instance.creator_verified:
        # Additional logic for verified creators can be added here
        pass

