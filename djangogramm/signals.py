from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os

from cloudinary import uploader

from .models import User, Media


@receiver(post_delete, sender=User)
def delete_avatar_file(sender, instance, **kwargs):
    if instance.avatar:
        uploader.destroy(instance.avatar.public_id)


@receiver(post_delete, sender=Media)
def delete_media_file(sender, instance, **kwargs):
    if instance.image:
        uploader.destroy(instance.image.public_id)
