from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post
from yatube.utils import paginate

User = get_user_model()


def index(request: object) -> Post:
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.all(),
            ),
        },
    )


def group_posts(request: object, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': paginate(
                request,
                group.posts.select_related('author').all(),
            ),
        },
    )


def profile(request: Any, username: Any) -> Any:
    user_author = get_object_or_404(User, username=username)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            author=user_author,
            user=request.user,
        ).exists()
    )
    return render(
        request,
        'posts/profile.html',
        {
            'page_obj': paginate(
                request,
                user_author.posts.all(),
            ),
            'user_name': user_author,
            'following': following,
        },
    )


def post_detail(request: Any, pk: Any) -> Any:
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': get_object_or_404(Post, pk=pk),
            'form': CommentForm(request.POST or None),
        },
    )


@login_required
def post_create(request: Any):
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
def post_edit(request: Any, pk: Any):
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
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
    page = paginate(
        request,
        Post.objects.filter(
            author__in=Follow.objects.filter(
                user_id=request.user.id,
            ).values('author_id')
        ).select_related('author'),
    )
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': page,
        },
    )


@login_required
def profile_follow(request: Any, username: Any):
    author_for_follow = get_object_or_404(User, username=username)
    if author_for_follow != request.user:
        Follow.objects.get_or_create(
            user=request.user, author=author_for_follow
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, user=request.user, author__username=username
    ).delete()
    return redirect('posts:follow_index')
