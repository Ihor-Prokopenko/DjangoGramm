from django.urls import path, include

from . import views
from base.settings import LOGIN_URL


urlpatterns = [
    path('', views.FeedPage.as_view(), name='feed'),
    path(
        'posts/',
        include(
            [
                path('details/<int:post_id>/', views.ShowPost.as_view(), name='single_post'),
                path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
                path('new_post/', views.CreatePost.as_view(), name='new_post'),
                path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
            ]
        ),
    ),
    path(
        'auth/',
        include(
            [
                path('login/', views.LoginUser.as_view(), name='login'),
                path('logout/', views.logout_user, name='logout'),
                path('register/', views.RegisterUser.as_view(), name='register'),
                path('activate/<uidb64>/<token>', views.activate, name='activate'),
                path('confirmation/', views.secondary_email_confirmation, name='secondary_email_confirmation'),
            ]
        ),
    ),
    path(
        'comments/',
        include(
            [
                path('comment_post/<int:post_id>/', views.CommentView.as_view(), name='comment_post'),
                path('comment_comment/<int:comment_id>/', views.CommentView.as_view(), name='comment_comment'),
                path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
            ]
        ),
    ),
    path(
        'profile/',
        include(
            [
                path('details/<int:pk>/', views.ShowProfile.as_view(), name='profile'),
                path('edit_profile/', views.EditProfile.as_view(), name='edit_profile'),
            ]
        ),
    ),
    path(
        'search/',
        include(
            [
                path('profile/', views.SearchProfile.as_view(), name='profile_search'),
                path('search/', views.search_recognizer, name='search_recognizer'),
            ]
        ),
    ),
    path(
        'interaction/',
        include(
            [
                path('like/<int:post_id>/', views.like_action, name='like'),
                path('save_post/<int:post_id>/', views.save_action, name='save_post'),
                path('follow/<int:user_id>/', views.follow_action, name='follow'),
                path('remove_tag/<int:post_id>/<str:tag_title>/', views.remove_tag, name='remove_tag'),
            ]
        ),
    ),

]
