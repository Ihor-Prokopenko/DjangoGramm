from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, View
from .forms import *
from .models import *


def search_recognizer(request):
    search_slug = request.GET.get('q')
    if not search_slug:
        return redirect('feed')
    if '@' == search_slug[0]:
        slug_clear = ''.join([slug for slug in search_slug.split('@') if slug])
        user = User.objects.filter(username=slug_clear).first()
        if user:
            return redirect('profile', pk=user.id)
        request.session['profile_slug'] = slug_clear
        return redirect('profile_search')

    request.session['search_slug'] = search_slug
    return redirect('feed')


class FeedPage(ListView):
    model = Post
    template_name = 'feed.html'
    context_object_name = 'posts'

    def get_queryset(self):
        search_slug = self.request.session.get('search_slug')
        if search_slug:
            return Post.objects.filter(tags__slug__icontains=search_slug).order_by('-date_created')
        search_slug = self.request.GET.get('tag')
        if search_slug:
            return Post.objects.filter(tags__slug__icontains=search_slug).order_by('-date_created')

        return Post.objects.all().order_by('-date_created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search_slug = self.request.session.get('search_slug')
        if not search_slug:
            search_slug = self.request.GET.get('tag')
        context['tag_slug'] = search_slug
        context['comment_form'] = CommentForm()
        self.request.session['search_slug'] = None   # cleaning session to work feed page correct after searching
        return context


class ShowPost(DetailView):
    model = Post
    template_name = 'single_post.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_tab = self.request.GET.get('active_tab')
        context['comment_form'] = CommentForm()
        return context


class CreatePost(CreateView):
    form_class = PostForm
    template_name = 'create_post.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()

        media_form = MediaForm(self.request.POST, self.request.FILES)
        if media_form.is_valid():
            images = [media_form.cleaned_data.get('image'),
                      media_form.cleaned_data.get('image2'),
                      media_form.cleaned_data.get('image3')]
            for image in images:
                if image:
                    Media.objects.create(image=image, post=post)
        post.generate_preview()
        tag_form = TagForm(self.request.POST)
        if tag_form.is_valid():
            tags = tag_form.cleaned_data.get('tags')
            tags_cleaned = [tag for tag in tags.split('#') if tag]
            for tag in tags_cleaned:
                tag_obj, created = Tag.objects.get_or_create(title=tag, slug=f'#{tag}')
                post.tags.add(tag_obj)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_form'] = MediaForm()
        context['tag_form'] = TagForm()
        return context

    def get_success_url(self):
        return reverse('single_post', kwargs={'post_id': self.object.pk})


class ShowProfile(DetailView):
    model = User
    template_name = 'profile.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_tab = self.request.GET.get('active_tab')
        context['profile'] = self.object
        context['active_tab'] = active_tab
        return context


class SearchProfile(ListView):
    model = User
    template_name = 'profile_search.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        profile_slug = self.request.session.get('profile_slug')
        if profile_slug:
            user_list = User.objects.filter(username__icontains=profile_slug).all()
            return user_list
        return User.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_slug = self.request.session.get('profile_slug')
        context['profile_slug'] = profile_slug
        self.request.session['profile_slug'] = None   # cleaning session to work feed page correct after searching
        return context


class RegisterUser(CreateView):
    form_class = SignUpForm
    template_name = 'register.html'

    def form_valid(self, form):
        if form.is_valid():
            user = form.save()
            login(self.request, user)
            messages.success(self.request, "You have successfully registered!")

            return redirect('profile', pk=user.id)


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_success_url(self):
        messages.success(self.request, "You have logged in!")
        return reverse_lazy('feed')


class CommentView(View):
    def post(self, request, post_id=None, comment_id=None):
        if not request.user.is_authenticated:
            redirect('feed')
        target = get_object_or_404(Post, id=post_id) if post_id else get_object_or_404(Comment, id=comment_id)

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            text = comment_form.cleaned_data.get('text')
            author = request.user

            if post_id:
                comment = Comment.objects.create(author=author,
                                                 text=text, target_post=get_object_or_404(Post, id=post_id))
            else:
                comment = Comment.objects.create(author=author,
                                                 text=text, target_comment=get_object_or_404(Comment, id=comment_id))

            redirect_target_id = target.id if post_id else comment.target_comment.target_post.id

            return redirect('single_post', redirect_target_id)


def logout_user(request):
    if not request.user.is_authenticated:
        return redirect('login')
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect('feed')


def delete_post(request, post_id=None):
    if not request.user.is_authenticated:
        return redirect('login')
    post = get_object_or_404(Post, pk=post_id)
    if request.user.id == post.author.id:
        post.delete()

    return redirect('feed')


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
    if not request.user.is_authenticated:
        return redirect('feed')
    post = get_object_or_404(Post, id=post_id)
    tag_obj = get_object_or_404(Tag, title=tag_title)
    if post and tag_obj and post.author.id == request.user.id:
        post.tags.remove(tag_obj)
    return redirect('feed')


def add_tag(request):
    pass


def delete_comment(request, comment_id):
    if not request.user.is_authenticated:
        return redirect('feed')
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user.id == comment.author.id:
        parent_post = comment.target_post if comment.target_post else comment.target_comment.target_post
        comment.delete()

        return redirect('single_post', parent_post.id)


def follow_action(request, user_id):
    if request.user.is_authenticated and request.user.id != user_id:
        target_user = get_object_or_404(User, pk=user_id)
        target_followers = target_user.followers.all()
        if request.user not in target_followers:
            target_user.followers.add(request.user)
        else:
            target_user.followers.remove(request.user)
        return redirect('profile', user_id)
    return redirect('feed')
