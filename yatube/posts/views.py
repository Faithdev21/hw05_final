from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginator_func

SAVE_GENERATED_PAGE_FOR = 20


@cache_page(SAVE_GENERATED_PAGE_FOR)
def index(request):
    template = "posts/index.html"
    posts = Post.objects.select_related("author", "group")
    context = {
        "page_obj": paginator_func(request, posts),
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("author")
    context = {
        "page_obj": paginator_func(request, posts),
        "group": group,
    }
    return render(request, template, context)


def profile(request, username):
    template = "posts/profile.html"
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related("group")
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = True
    context = {
        "author": author,
        "page_obj": paginator_func(request, posts),
        "following": following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    context = {
        "post": post,
        "form": form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = "posts/create_post.html"

    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", post.author.username)
    form = PostForm()

    context = {"form": form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = "posts/create_post.html"
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect("posts:post_detail", post.pk)
    context = {"form": form, "post": post, "is_edit": True}
    return render(request, template, context)


@login_required()
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required()
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user).select_related('author')
    template = 'posts/follow.html'
    context = {
        'page_obj': paginator_func(request, posts),
        'follow': True,
    }
    return render(request, template, context)


@login_required()
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required()
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', author)
