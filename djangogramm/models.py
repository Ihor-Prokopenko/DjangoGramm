from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
import os

from django.urls import reverse

NO_USER_AVATAR = os.getenv('NO_USER_AVATAR')
USER_AVATAR_UPLOAD = os.getenv('USER_AVATAR_UPLOAD')
POST_IMAGES_UPLOAD = os.getenv('POST_IMAGES_UPLOAD')


class User(AbstractUser):
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to=USER_AVATAR_UPLOAD, default=NO_USER_AVATAR, blank=True)
    followers = models.ManyToManyField('self', related_name='follows', blank=True, null=True, symmetrical=False)

    def save(self, *args, **kwargs):
        try:
            old_self = User.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            old_self = None

        if old_self and old_self.avatar != self.avatar and old_self.avatar != NO_USER_AVATAR:
            if old_self.avatar and os.path.isfile(old_self.avatar.path):
                os.remove(old_self.avatar.path)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"@{self.username}"


@receiver(post_delete, sender=User)
def delete_avatar_file(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path) and instance.avatar != NO_USER_AVATAR:
            os.remove(instance.avatar.path)


class Tag(models.Model):
    title = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(max_length=25, unique=True, blank=True)

    def __str__(self):
        return f"#{self.title}"


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    description = models.CharField(max_length=255, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    date_created = models.DateTimeField(User, auto_now_add=True)
    date_modified = models.DateTimeField(User, auto_now=True, blank=True)
    likes = models.ManyToManyField(User, blank=True, related_name='liked')

    def __str__(self):
        return f"Post {self.id}"

    def get_absolute_url(self):
        return reverse('single_post', args=[self.pk])

    def get_total_comments_count(self):
        count = self.comments.count()
        for comment in self.comments.all():
            count += comment.get_total_comments_count()
        return count


class Media(models.Model):
    image = models.ImageField(upload_to=POST_IMAGES_UPLOAD)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return f"Image of {self.post}"


@receiver(post_delete, sender=Media)
def delete_media_file(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.CharField(max_length=255, blank=False)
    target_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    target_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment {self.id}"

    def get_total_comments_count(self):
        count = self.comments.count()
        for comment in self.comments.all():
            count += comment.get_total_comments_count()
        return count
