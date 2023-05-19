from django.urls import path
from . import views


urlpatterns = [
    path('', views.FeedPage.as_view(), name='feed'),
    path('post/<int:post_id>/', views.ShowPost.as_view(), name='single_post'),
    path('new_post/', views.CreatePost.as_view(), name='new_post'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('like/<int:post_id>/', views.like_action, name='like'),
    path('follow/<int:user_id>/', views.follow_action, name='follow'),
    path('profile/<int:pk>/', views.ShowProfile.as_view(), name='profile'),
    path('remove_tag/<int:post_id>/<str:tag_title>/', views.remove_tag, name='remove_tag'),
    path('comment_post/<int:post_id>/', views.CommentView.as_view(), name='comment_post'),
    path('comment_comment/<int:comment_id>/', views.CommentView.as_view(), name='comment_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('search/', views.search_recognizer, name='search_recognizer'),
]
