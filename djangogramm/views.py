from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView

from .forms import *
from .models import *


def search_recognizer(request):
    search_slug = request.GET.get('q')
    url = reverse('feed')

    if not search_slug:
        return redirect(url)

    if '@' == search_slug[0]:
        slug_clear = ''.join([slug for slug in search_slug.split('@') if slug])
        user = User.objects.filter(username=slug_clear).first()
        if user:
            return redirect('profile', pk=user.id)
        return redirect(reverse('profile_search') + f'?username={slug_clear}')

    elif '#' == search_slug[0]:
        slug_clear = ''.join([slug for slug in search_slug.split('#') if slug])
        url += f'?tag={slug_clear}'
    return redirect(url)


def edit_post(request, post_id):
    post_obj = get_object_or_404(Post, id=post_id)
    if request.method == "POST" and request.user.id == post_obj.author.id:
        description = request.POST.get('description')
        tags = request.POST.get('tags')
        tags_cleaned = [tag for tag in tags.split('#') if tag]
        post_obj.tags.clear()
        for tag in tags_cleaned:
            tag_obj, created = Tag.objects.get_or_create(title=tag, slug=f'#{tag}')
            post_obj.tags.add(tag_obj)

        post_obj.description = description
        post_obj.save()

        return redirect('single_post', post_id=post_id)


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

    if not post.likes.filter(id=request.user.id).exists():
        post.likes.add(request.user)
        return redirect('single_post', post_id)
    post.likes.remove(request.user)
    return redirect('single_post', post_id)


def save_action(request, post_id):
    if not request.user.is_authenticated:
        return redirect('login')
    post = get_object_or_404(Post, id=post_id)

    if not post.saved.filter(id=request.user.id).exists():
        post.saved.add(request.user)
        return redirect('single_post', post_id)
    post.saved.remove(request.user)
    return redirect('single_post', post_id)


def remove_tag(request, post_id, tag_title):
    if not request.user.is_authenticated:
        return redirect('feed')
    post = get_object_or_404(Post, id=post_id)
    tag_obj = get_object_or_404(Tag, title=tag_title)
    if post and tag_obj and post.author.id == request.user.id:
        post.tags.remove(tag_obj)
    return redirect('feed')


def delete_comment(request, comment_id):
    if not request.user.is_authenticated:
        return redirect('feed')
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user.id == comment.author.id or request.user.id == comment.by_post.author.id:
        parent_post = comment.target_post if comment.target_post else comment.target_comment.target_post
        comment.delete()

        return redirect('single_post', parent_post.id)


def follow_action(request, user_id):
    if not request.user.is_authenticated or request.user.id == user_id:
        return redirect('feed')
    target_user = get_object_or_404(User, pk=user_id)
    target_followers = target_user.followers.all()

    if request.user not in target_followers:
        target_user.followers.add(request.user)
        return redirect('profile', user_id)
    target_user.followers.remove(request.user)
    return redirect('profile', user_id)


class FeedPage(ListView):
    model = Post
    template_name = 'feed.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self):
        search_slug = self.request.GET.get('tag')
        if not search_slug:
            return Post.objects.all().order_by('-date_created')
        return Post.objects.filter(tags__slug__icontains=search_slug).order_by('-date_created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search_slug = self.request.session.get('search_slug')
        if not search_slug:
            search_slug = self.request.GET.get('tag')
        context['tag_slug'] = search_slug
        context['comment_form'] = CommentForm()
        context['edit_post_form'] = EditPostForm()
        return context


class ShowPost(DetailView):
    model = Post
    template_name = 'single_post.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        data_list = self.object.saved.all() \
            if active_tab == 'favourites' \
            and self.request.user.id == self.object.id \
            else self.object.posts.all()

        page_number = self.request.GET.get('page')
        paginator = Paginator(data_list, 6)
        page_obj = paginator.get_page(page_number)

        context['profile'] = self.object
        context['active_tab'] = active_tab
        context['page_obj'] = page_obj
        context['comment_form'] = CommentForm()
        return context


class EditProfile(UpdateView):
    form_class = EditProfileForm
    template_name = 'edit_profile.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        profile_id = self.request.user.id
        return reverse('profile', kwargs={'pk': profile_id})


class SearchProfile(ListView):
    paginate_by = 5
    model = User
    template_name = 'profile_search.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        profile_slug = self.request.GET.get('username')
        if not profile_slug:
            return User.objects.all()
        user_list = User.objects.filter(username__icontains=profile_slug).all()
        return user_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_slug = self.request.GET.get('username')
        context['profile_slug'] = profile_slug
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

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            text = comment_form.cleaned_data.get('text')
            print(text)
            author = request.user

            if post_id:
                target_post = get_object_or_404(Post, id=post_id)
                comment = Comment.objects.create(author=author,
                                                 text=text, target_post=target_post, by_post=target_post)
            elif comment_id:
                target_comment = get_object_or_404(Comment, id=comment_id, )
                comment = Comment.objects.create(author=author,
                                                 text=text, target_comment=target_comment,
                                                 by_post=target_comment.by_post)

            redirect_target_id = post_id if post_id else comment.by_post.id

            return redirect('single_post', redirect_target_id)
