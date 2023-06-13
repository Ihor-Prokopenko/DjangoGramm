# DB
Choice is MySQL to try first time with it.


# 1. Create django project:

- Adjust settings
- Define static/media dirs/urls
- Set database connection
- Create DjangoGramm app
- Register app at settings.py

# 2. Create models

## CustomUser:
- username
- email
- password
- full_name
- bio
- avatar

## Post:
- author = ForeignKey(CustomUser)
- description
- tags = ManyToManyField(Tag)

## Media:
- image
- post = ForeignKey(Post)

## Tag:
- title

## Like:
- liker = ForeignKey(CustomUser, related_name='likes')
- target = ForeignKey(Post, related_name='likes')

## Comment:
- author = ForeignKey(CustomUser)
- text
- target = ForeignKey(Post)

## Follow:
- follower = ForeignKey(CustomUser, related_name='followers')
- target = ForeignKey(CustomUser, related_name='followers')

# 3. Create Forms

- Login
- Register
- EditProfile
- CreatePost
- Comment

# 4. Create Routes and Views
- Login/logout
- Register/ConfirmEmail
- Profile
- Post/CreatePost
- Feed

*as needed routes*

*in the process it will be clear which method will be for these functions*

- Add/Remove

  - Like
  - Follow
  - Comment
  - Delete post

# 5. Invent Preview functionality

~

# 6. Fill database with fake data, then test it work


~

# 7. Deploy project to the server

~
