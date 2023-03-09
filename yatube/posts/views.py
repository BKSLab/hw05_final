from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post
from yatube.utils import paginate

User = get_user_model()


def index(request: object) -> Post:
    posts = Post.objects.all()
    page = paginate(request, posts)
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': page,
        },
    )


def group_posts(request: object, slug: str) -> Group:
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()
    page = paginate(request, posts)
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': page,
        },
    )


def profile(request: Any, username: Any) -> Any:
    user_name = get_object_or_404(User, username=username)
    posts = user_name.posts.all()
    page = paginate(request, posts)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=user_name, user=request.user
        ).exists()
    return render(
        request,
        'posts/profile.html',
        {
            'page_obj': page,
            'user_name': user_name,
            'following': following,
        },
    )


def post_detail(request: Any, pk: Any) -> Any:
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    return render(
        request,
        'posts/post_detail.html',
        {
            'comments': comments,
            'post': post,
            'form': form,
        },
    )


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {
                'form': form,
            },
        )
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if request.user != post.author:
        return redirect('posts:post_detail', pk)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', pk)
    return render(
        request,
        'posts/create_post.html',
        {
            'is_edit': True,
            'post': post,
            'form': form,
        },
    )


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', pk)


@login_required
def follow_index(request):
    authors = Follow.objects.filter(user_id=request.user.id).values(
        'author_id'
    )
    posts = Post.objects.filter(author__in=authors).select_related('author')
    page = paginate(request, posts)
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': page,
        },
    )


@login_required
def profile_follow(request, username):
    author_for_follow = get_object_or_404(User, username=username)
    if author_for_follow != request.user:
        Follow.objects.get_or_create(
            user=request.user, author=author_for_follow
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    follow_on_author = get_object_or_404(
        Follow, user=request.user, author__username=username
    )
    follow_on_author.delete()
    return redirect('posts:follow_index')
