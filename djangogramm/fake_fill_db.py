from djangogramm.models import *
import os
from pathlib import Path
from PIL import Image
from base.settings import *
import random
from faker import Faker


FAKE_AVATARS_DIR = 'fake/fake_avatars/'
FAKE_POST_IMAGES_DIR = 'fake/fake_post_images/'


AVATAR_FILES_LIST = os.listdir(MEDIA_URL + FAKE_AVATARS_DIR)
POST_FILES_LIST = os.listdir(MEDIA_URL + FAKE_POST_IMAGES_DIR)

username_list = []
fake = Faker()
fake_tags = [fake.word().lower() for i in range(30)]
image_choices_list = []


def create_fake_user(avatar_filename=None):
    if not avatar_filename:
        return False
    avatar_file = Image.open(os.path.join(MEDIA_ROOT, FAKE_AVATARS_DIR, avatar_filename))
    avatar_path = os.path.join(MEDIA_ROOT, USER_AVATAR_UPLOAD, avatar_filename)
    avatar_file.save(avatar_path)
    avatar_db_path = os.path.join(USER_AVATAR_UPLOAD, avatar_filename)

    username = fake.user_name()
    email = f'{username}@gmail.com'
    password = f'{username}password'
    full_name = fake.name()
    bio = fake.sentence(nb_words=random.randint(15, 30))
    user = User.objects.create_user(username=username,
                                    email=email,
                                    password=password,
                                    bio=bio,
                                    avatar=avatar_db_path,
                                    full_name=full_name,
    )
    if user:
        print(f"User '{user.username}' created!")
        username_list.append(user.username)
        return user.username
    else:
        print("There was an error!")
        return False


def create_media(post_id):
    post = Post.objects.filter(pk=post_id).first()
    if not post:
        return False
    filename = random.choice(POST_FILES_LIST)
    if filename in image_choices_list:
        while filename in image_choices_list:
            filename = random.choice(POST_FILES_LIST)
            if len(image_choices_list) >= len(POST_FILES_LIST):
                image_choices_list.clear()
    image_choices_list.append(filename)
    file = Image.open(os.path.join(MEDIA_ROOT, FAKE_POST_IMAGES_DIR, filename))
    filepath = os.path.join(MEDIA_ROOT, POST_IMAGES_UPLOAD, filename)
    if os.path.isfile(filepath):
        filename = f'{random.randint(100, 1000)}' + filename
        filepath = os.path.join(MEDIA_ROOT, POST_IMAGES_UPLOAD, filename)
    file.save(filepath)
    file_db_path = os.path.join(POST_IMAGES_UPLOAD, filename)

    media = Media.objects.create(image=file_db_path, post=post)
    if not media:
        return False


def create_fake_post(username=None):
    username = username
    user = User.objects.filter(username=username).first()
    if not user:
        print(f"There was an error finding user {username}!")
        return False
    description = fake.sentence(nb_words=random.randint(10, 25))
    if len(description) > 254:
        while description >= 255:
            description = fake.sentence(nb_words=random.randint(10, 25))
    post = Post.objects.create(author=user, description=description)
    for media in range(1, random.randint(2, 4)):
        create_media(post_id=post.id)
    if post.images.exists():
        post.generate_preview()

    tags = random.choices(fake_tags, k=random.randint(3, 5))
    for tag in tags:
        tag_obj, created = Tag.objects.get_or_create(title=tag, slug=f'#{tag}')
        post.tags.add(tag_obj)
    post.save()
    image_count = post.images.count()
    tag_count = post.tags.count()
    print(f"Post id:{post.id} created! Images:{image_count},"
          f" Tags:{tag_count}| {post.author.username}: {post.author.posts.count()}")


def create_users():
    for avatar in AVATAR_FILES_LIST:
        create_fake_user(avatar_filename=avatar)


def create_posts():
    users = User.objects.filter(is_staff=False).all()
    if not users:
        return False
    for post in range(1, random.randint(35, 50)):
        user = random.choice(users)
        create_fake_post(username=user.username)


def main():
    create_users()
    create_posts()


if __name__ == '__main__':
    main()
