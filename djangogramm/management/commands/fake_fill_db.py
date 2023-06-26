from djangogramm.models import *
from base.settings.base import *
import random
from io import BytesIO

from PIL import Image
from faker import Faker

USERS_NUM = 5
POSTS_NUM = random.randint(15, 20)

username_list = []
fake = Faker()
fake_tags = [fake.word().lower() for i in range(30)]
generators = []


def register_generator(dep=None):
    def wrapper(generator_func):
        generator_func.dep = dep
        generators.append(generator_func)
        return generator_func

    return wrapper


def create_image(width, height):
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    color = (red, green, blue)

    image = Image.new("RGB", (width, height), color)

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def create_fake_user():
    width, height = AVATAR_IMAGE_SIZE
    created_image = create_image(width, height)

    username = fake.user_name()
    email = f'{username}@gmail.com'
    password = f'{username}password'
    full_name = fake.name()
    bio = fake.sentence(nb_words=random.randint(15, 30))

    upload_result = cloudinary.uploader.upload(created_image,
                                               transformation=[
                                                   {'width': 200, 'height': 200, 'crop': 'fill'}
                                               ])
    avatar_url = upload_result['public_id'] if upload_result['public_id'] else None

    user = User.objects.create_user(username=username,
                                    email=email,
                                    password=password,
                                    bio=bio,
                                    avatar=avatar_url,
                                    full_name=full_name,
                                    )
    if user:

        username_list.append(user.username)
        return user
    else:
        print("There was an error!")
        return False


def create_media(post_id):
    post = Post.objects.filter(pk=post_id).first()
    if not post:
        return False
    width, height = POST_IMAGE_SIZE
    created_image = create_image(width, height)

    upload_result = cloudinary.uploader.upload(created_image,
                                               transformation=[
                                                   {
                                                       'height': 700,
                                                       'crop': 'scale',
                                                   }
                                               ])
    file_url = upload_result['public_id'] if upload_result['public_id'] else None

    media = Media.objects.create(image=file_url, post=post)
    if not media:
        return False
    return True


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
    if post.images:
        post.generate_preview()

    tags = random.choices(fake_tags, k=random.randint(3, 5))
    for tag in tags:
        tag_obj, created = Tag.objects.get_or_create(title=tag, slug=f'#{tag}')
        post.tags.add(tag_obj)
    post.save()
    image_count = post.images.count()
    tag_count = post.tags.count()
    return post


@register_generator()
def generate_users():
    curr_user_count = 1
    for avatar in range(1, USERS_NUM + 1):
        user = create_fake_user()
        if user:
            print(f"{curr_user_count}/{USERS_NUM} User '{user.username}' created!")
            curr_user_count += 1
    return True


@register_generator(dep=generate_users)
def generate_posts():
    users = User.objects.filter(is_staff=False).all()
    if not users:
        return False
    curr_posts_count = 1
    for post in range(1, POSTS_NUM + 1):
        user = random.choice(users)
        post = create_fake_post(username=user.username)
        if post:
            images_count = post.images.count()
            tag_count = post.tags.count()
            print(f"{curr_posts_count}/{POSTS_NUM} Post id:{post.id} created! Images:{images_count},"
                  f" Tags:{tag_count}| {post.author.username}: {post.author.posts.count()}")
            curr_posts_count += 1

    return True


@register_generator(dep=(generate_users, generate_posts))
def generate_likes():
    users = User.objects.filter(is_staff=False).all()
    posts = Post.objects.filter().all()
    likes_num = 0
    for user in users:
        for post in posts:
            action = random.choice([True, False])
            if action and not post.likes.filter(id=user.id).exists():
                post.likes.add(user)
                likes_num += 1
    print(f"{likes_num} likes generated!")
    return True


@register_generator(dep=(generate_users, generate_posts))
def generate_favourites():
    users = User.objects.filter(is_staff=False).all()
    posts = Post.objects.filter().all()
    favourites_num = 0
    for user in users:
        for post in posts:
            action = random.choice([True, False])
            if action and not post.saved.filter(id=user.id).exists():
                post.saved.add(user)
                favourites_num += 1
    print(f"{favourites_num} favourites generated!")
    return True


@register_generator(dep=generate_users)
def generate_follows():
    users = User.objects.filter(is_staff=False).all()
    follows_num = 0
    for user in users:
        for target in users:
            action = random.choice([True, False])
            if action and user.id != target.id:
                target.followers.add(user)
                follows_num += 1
    print(f"{follows_num} follows generated!")
    return True


@register_generator(dep=(generate_users, generate_posts))
def generate_comments():
    posts = Post.objects.filter().all()
    users = User.objects.filter(is_staff=False).all()
    if not posts or not users:
        return False
    comments_count = 0
    for post in posts:
        comments_num = random.randint(1, 5)
        for i in range(1, comments_num + 1):
            author = random.choice(users)
            text = fake.sentence(nb_words=random.randint(5, 15))
            Comment.objects.create(author=author,
                                   text=text, target_post=post, by_post=post)
            comments_count += 1
    print(f"{comments_count} comments generated!")
    return True


@register_generator(dep=(generate_users, generate_posts))
def generate_answers():
    comments = Comment.objects.filter().all()
    users = User.objects.filter(is_staff=False).all()
    if not comments or not users:
        return False
    answers_count = 0
    for comment in comments:
        answers_num = random.randint(1, 3)
        for i in range(1, answers_num + 1):
            author = random.choice(users)
            text = fake.sentence(nb_words=random.randint(5, 15))
            Comment.objects.create(author=author,
                                   text=text, target_comment=comment, by_post=comment.by_post)
            answers_count += 1
    print(f"{answers_count} answers generated!")
    return True


def main():
    if not generators:
        return False
    for generator in generators:
        generator()
    return True


if __name__ == '__main__':
    main()
