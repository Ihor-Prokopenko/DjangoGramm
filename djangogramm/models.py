from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
import os

from PIL import Image

from base.settings.base import *

TAG_STR_DISPLAY = "#{title}"
USER_STR_DISPLAY = "@{username}"


class User(AbstractUser):
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to=USER_AVATAR_UPLOAD, default=NO_USER_AVATAR)
    followers = models.ManyToManyField('self', related_name='follows', blank=True, null=True, symmetrical=False)

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)
        if self.avatar and self.avatar != NO_USER_AVATAR:
            image = Image.open(self.avatar.path)

            target_width, target_height = AVATAR_IMAGE_SIZE

            aspect_ratio = AVATAR_ASPECT_RATIO
            width, height = image.size
            image_aspect_ratio = width / height

            if image_aspect_ratio > aspect_ratio:
                new_width = int(height * aspect_ratio)
                left = (width - new_width) // 2
                right = left + new_width
                image = image.crop((left, 0, right, height))
            elif image_aspect_ratio < aspect_ratio:
                new_height = int(width / aspect_ratio)
                top = (height - new_height) // 2
                bottom = top + new_height
                image = image.crop((0, top, width, bottom))

            image = image.resize((target_width, target_height), Image.ANTIALIAS)
            image = image.convert('RGB')

            avatar_filename = f'avatar_{self.username}.jpg'
            avatar_path = os.path.join(MEDIA_ROOT, USER_AVATAR_UPLOAD, avatar_filename)

            image.save(avatar_path, format='JPEG')

            if self.avatar and self.avatar != os.path.join(USER_AVATAR_UPLOAD,
                                                           avatar_filename) and os.path.isfile(
                self.avatar.path) and self.avatar != NO_USER_AVATAR:
                os.remove(self.avatar.path)

            self.avatar.name = os.path.join(USER_AVATAR_UPLOAD, avatar_filename)
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
    preview = models.ImageField(upload_to=POST_IMAGES_UPLOAD, default=NO_PREVIEW_IMAGE, blank=True)

    class Meta:
        ordering = ['-date_created']

    def generate_preview(self):
        post_media = self.images.first()

        if post_media and post_media.image.path != self.preview.path:
            image = Image.open(post_media.image.path)

            target_width, target_height = POST_PREVIEW_SIZE

            aspect_ratio = POST_PREVIEW_ASPECT_RATIO
            width, height = image.size
            image_aspect_ratio = width / height

            if image_aspect_ratio > aspect_ratio:
                new_width = int(height * aspect_ratio)
                left = (width - new_width) // 2
                right = left + new_width
                image = image.crop((left, 0, right, height))
            elif image_aspect_ratio < aspect_ratio:
                new_height = int(width / aspect_ratio)
                top = (height - new_height) // 2
                bottom = top + new_height
                image = image.crop((0, top, width, bottom))

            image = image.resize((target_width, target_height), Image.ANTIALIAS)
            image = image.convert('RGB')

            preview_filename = f'preview_{self.id}.jpg'
            preview_path = os.path.join(MEDIA_ROOT, POST_IMAGES_UPLOAD, preview_filename)

            image.save(preview_path, format='JPEG')
            self.preview.name = os.path.join(POST_IMAGES_UPLOAD, preview_filename)
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
        height_list = []
        for image in self.images.all():
            width, height = Image.open(image.image.path).size
            height_list.append(int(height))
        return max(height_list)


class Media(models.Model):
    image = models.ImageField(upload_to=POST_IMAGES_UPLOAD)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='images')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

        img.thumbnail(POST_IMAGE_SIZE)
        img = img.convert('RGB')
        img.save(self.image.path, format='JPEG')


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
