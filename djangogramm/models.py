from cloudinary.api import resource
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
import os

from cloudinary.models import CloudinaryField
from cloudinary import uploader, CloudinaryImage

from base.settings.base import *

TAG_STR_DISPLAY = "#{title}"
USER_STR_DISPLAY = "@{username}"


class User(AbstractUser):
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    avatar = CloudinaryField('image', blank=True, transformation={
        'width': AVATAR_IMAGE_SIZE[0],
        'height': AVATAR_IMAGE_SIZE[1],
        'crop': 'fill',
    })
    followers = models.ManyToManyField('self', related_name='follows', blank=True, null=True, symmetrical=False)

    def save(self, *args, **kwargs):
        try:
            this = User.objects.get(id=self.id)
            if this.avatar != self.avatar and this.avatar:
                uploader.destroy(this.avatar.public_id)
        except User.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return USER_STR_DISPLAY.format(username=self.username)


class Tag(models.Model):
    title = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(max_length=25, unique=True, blank=True)

    def __str__(self):
        return TAG_STR_DISPLAY.format(title=self.title)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    description = models.CharField(max_length=255, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    date_created = models.DateTimeField(User, auto_now_add=True)
    date_modified = models.DateTimeField(User, auto_now=True, blank=True)
    likes = models.ManyToManyField(User, blank=True, related_name='liked')
    saved = models.ManyToManyField(User, blank=True, related_name='saved')
    preview = models.CharField(max_length=255, blank=True)
    max_image_height = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-date_created']

    def generate_preview(self):
        height_list = []
        images = self.images.all()
        for image in images:
            image_info = resource(image.image.public_id)
            height = image_info.get('height', 0)
            height_list.append(int(height))
        self.max_image_height = max(height_list)

        post_media = self.images.first()

        if post_media:
            image = CloudinaryImage(post_media.image.public_id)
            width, height = POST_PREVIEW_SIZE
            url = image.build_url(transformation={
                'crop': 'fill',
                'width': width,
                'height': height,
                'format': 'jpg',
            }, secure=False)
            self.preview = url
            self.save()

    def get_tags_string(self):
        tags = self.tags.all()
        tag_list = []
        for tag in tags:
            tag_list.append(tag.__str__())

        return ''.join(tag_list)

    def get_absolute_url(self):
        return reverse('single_post', args=[self.pk])

    def get_total_comments_count(self):
        count = self.comments.count()
        for comment in self.comments.all():
            count += comment.get_total_comments_count()
        return count

    def get_max_height_image(self):
        return self.max_image_height


class Media(models.Model):
    image = CloudinaryField('image', transformation={
        'height': POST_IMAGE_SIZE[1],
        'crop': 'scale',
    })
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='images')


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.CharField(max_length=255, blank=False)
    target_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    target_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    by_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='all_comments', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def get_total_comments_count(self):
        count = self.comments.count()
        for comment in self.comments.all():
            count += comment.get_total_comments_count()
        return count

    class Meta:
        ordering = ['-date_created']
