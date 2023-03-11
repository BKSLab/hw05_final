from django.urls import path

from posts import views

app_name = '%(posts_label)s'

urlpatterns = [
    path('', views.index, name='h_page'),
    path('create/', views.post_create, name='post_create'),
    path('follow/', views.follow_index, name='follow_index'),
    path('group/<slug:slug>/', views.group_posts, name='page_post'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow',
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow',
    ),
    path('posts/<int:pk>/comment/', views.add_comment, name='add_comment'),
]
