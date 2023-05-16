from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('filter/', views.home, name='filtered_home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('new_post/', views.create_post, name='new_post'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('like/<int:post_id>/', views.like_action, name='like'),
    path('follow/<int:user_id>/', views.follow_action, name='follow'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('remove_tag/<int:post_id>/<str:tag_title>/', views.remove_tag, name='remove_tag'),
    path('comment_post/<int:post_id>/', views.comment_post, name='comment_post'),
    path('comment_comment/<int:comment_id>/', views.comment_comment, name='comment_comment'),
    path('post/<int:post_id>/', views.single_post, name='single_post'),
]
