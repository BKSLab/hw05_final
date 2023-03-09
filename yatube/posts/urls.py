from django.urls import path

from posts.views import (
    add_comment,
    follow_index,
    group_posts,
    index,
    post_create,
    post_detail,
    post_edit,
    profile,
    profile_follow,
    profile_unfollow,
)

app_name = '%(posts_label)s'

urlpatterns = [
    path('', index, name='h_page'),
    path('create/', post_create, name='post_create'),
    path('follow/', follow_index, name='follow_index'),
    path('group/<slug:slug>/', group_posts, name='page_post'),
    path('posts/<int:pk>/', post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', post_edit, name='post_edit'),
    path('profile/<str:username>/', profile, name='profile'),
    path(
        'profile/<str:username>/follow/', profile_follow, name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        profile_unfollow,
        name='profile_unfollow',
    ),
    path('posts/<int:pk>/comment/', add_comment, name='add_comment'),
]
