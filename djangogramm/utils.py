from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

from base.settings import NO_USER_AVATAR, NO_PREVIEW_IMAGE


def delete_avatar_file(sender, instance, **kwargs):
    if not instance.avatar:
        raise FileExistsError
    if os.path.isfile(instance.avatar.path) and instance.avatar != NO_USER_AVATAR:
        os.remove(instance.avatar.path)


def delete_media_file(sender, instance, **kwargs):
    if not instance.image:
        raise FileExistsError
    if os.path.isfile(instance.image.path):
        os.remove(instance.image.path)


def delete_preview_file(sender, instance, **kwargs):
    if not instance.preview:
        raise FileExistsError
    if os.path.isfile(instance.preview.path) and instance.preview != NO_PREVIEW_IMAGE:
        os.remove(instance.preview.path)
