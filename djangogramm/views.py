from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . forms import *
from . models import *


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    tag = request.GET.get('tag')
    fltr = ''
    if tag:
        tag_cleaned = [t for t in tag.split('#') if t][0]
        tag_obj = Tag.objects.filter(title=tag_cleaned).first()
        if tag_obj:
            posts = tag_obj.posts.all().order_by('-date_created')
        else:
            posts = []
        fltr = tag
    else:
        posts = Post.objects.all().order_by('-date_created')

    tag_form = TagForm()
    comment_form = CommentForm()\

    context = {
        'posts': posts,
        'tag_form': tag_form,
        'comment_form': comment_form,
        'fltr': fltr,
    }
    return render(request, 'home.html', context)


def profile(request, pk):
    if not request.user.is_authenticated:
        return redirect('home')

    profile_user = get_object_or_404(CustomUser, id=pk)
    posts = profile_user.posts.all().order_by('-date_created')
    context = {
        'profile': profile_user,
        'posts': posts,
        'comments': 1,
    }
    return render(request, 'profile.html', context)


def create_post(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        form = PostForm(request.POST)
        media_form = MediaForm(request.POST, request.FILES)
        tag_form = TagForm(request.POST)
        if form.is_valid() and media_form.is_valid() and tag_form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            images = [media_form.cleaned_data.get('image'),
                      media_form.cleaned_data.get('image2'),
                      media_form.cleaned_data.get('image3')]
            if images:
                for image in images:
                    if image:
                        Media.objects.create(image=image, post=post)
            tags = tag_form.cleaned_data.get('tags')
            tags_cleaned = [tag for tag in tags.split('#') if tag]
            if tags_cleaned:
                for tag in tags_cleaned:
                    tag_obj, created = Tag.objects.get_or_create(title=tag, slug=tag)
                    post.tags.add(tag_obj)
            messages.success(request, "You have successfully created publication!")
            return redirect('home')

    form = PostForm()
    media_form = MediaForm()
    tag_form = TagForm()
    context = {
        'form': form,
        'media_form': media_form,
        'tag_form': tag_form,
    }

    return render(request, 'create_post.html', context)


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have logged in!")
            return redirect('home')
        else:
            messages.success(request, "There was an error logging in, please try again!")
            return redirect('login')
    return render(request, 'login.html')


def logout_user(request):
    if not request.user.is_authenticated:
        return redirect('login')
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You have successfully registered!")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})


def delete_post(request, post_id=None):
    if not request.user.is_authenticated:
        return redirect('login')
    post = get_object_or_404(Post, pk=post_id)
    if request.user.id == post.author.id:
        post.delete()

    return redirect('home')


def like_action(request, post_id):
    if not request.user.is_authenticated:
        return redirect('login')
    post = get_object_or_404(Post, id=post_id)

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return redirect('single_post', post_id)


def remove_tag(request, post_id, tag_title):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        tag_obj = get_object_or_404(Tag, title=tag_title)
        if post and tag_obj:
            post.tags.remove(tag_obj)
        return redirect('home')
    return redirect('home')


def add_tag(request):
    pass


def comment_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user.is_authenticated:
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                text = comment_form.cleaned_data.get('text')
                author = request.user

                comment = Comment.objects.create(author=author, text=text, target_post=post)

                return redirect('single_post', post_id)

    return redirect('home')


def comment_comment(request, comment_id):
    comment_target = get_object_or_404(Comment, id=comment_id)
    if request.user.is_authenticated:
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                text = comment_form.cleaned_data.get('text')
                author = request.user

                comment = Comment.objects.create(author=author, text=text, target_comment=comment_target)

                return redirect('single_post', post_id=comment_target.target_post.id)

    return redirect('home')


def single_post(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=post_id)
        comment_form = CommentForm()
        context = {
            'post': post,
            'comment_form': comment_form,
        }
        return render(request, 'single_post.html', context)
    return redirect('home')


def follow_action(request, user_id):
    if request.user.is_authenticated and request.user.id != user_id:
        target_user = get_object_or_404(CustomUser, pk=user_id)
        target_followers = target_user.followers.all()
        if request.user not in target_followers:
            target_user.followers.add(request.user)
        else:
            target_user.followers.remove(request.user)
        return redirect('profile', user_id)
    return redirect('home')
