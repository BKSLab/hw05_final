from django.contrib import admin

from posts.models import Comment, Follow, Group, Post
from yatube.admin import BaseAdmin


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)


@admin.register(Group)
class GroupAdmin(BaseAdmin):
    list_display = (
        'title',
        'slug',
        'description',
    )
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = (
        'pk',
        'post',
        'author',
        'text',
    )
    search_fields = (
        'pk',
        'text',
        'author',
    )
    list_filter = (
        'text',
        'created',
    )


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = (
        'user',
        'author',
    )
    list_filter = (
        'user',
        'author',
    )
