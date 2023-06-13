from django.urls import path, include

from . import views
from base.settings.base import LOGIN_URL

urlpatterns = [
    path('', views.FeedPage.as_view(), name='feed'),
    path(
        'post/',
        include(
            [
                path('<int:post_id>/', views.ShowPost.as_view(), name='single_post'),
                path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
                path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
                path('create/', views.CreatePost.as_view(), name='new_post'),
                path('<int:post_id>/comment/', views.CommentView.as_view(), name='comment_post'),
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
        'comment/',
        include(
            [
                path('<int:comment_id>/answer/', views.CommentView.as_view(), name='comment_comment'),
                path('<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
            ]
        ),
    ),
    path(
        'profile/',
        include(
            [
                path('details/<int:pk>/', views.ShowProfile.as_view(), name='profile'),
                path('edit/', views.EditProfile.as_view(), name='edit_profile'),
            ]
        ),
    ),
    path(
        'search/',
        include(
            [
                path('profile/', views.SearchProfile.as_view(), name='profile_search'),
                path('index/', views.search_recognizer, name='search_recognizer'),
            ]
        ),
    ),
    path(
        'interaction/',
        include(
            [
                path('<int:post_id>/like/', views.like_action, name='like'),
                path('<int:post_id>/save/', views.save_action, name='save_post'),
                path('<int:user_id>/follow/', views.follow_action, name='follow'),
                path('<int:post_id>/remove_tag/<str:tag_title>/', views.remove_tag, name='remove_tag'),
            ]
        ),
    ),

]
