
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Post, Group, Follow
from .forms import PostForm, User, CommentForm
from .utils import pagination

POST_ON_PAGE: int = 10


def index(request):
    """Вывод на главную страницу 10 последних постов."""
    template = 'posts/index.html'
    post_list = Post.objects.select_related()
    page_obj = pagination(post_list, request, POST_ON_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Вывод на страницу 10 постов группы."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = pagination(post_list, request, POST_ON_PAGE)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Вывод на страницу 10 постов пользователя"""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author__username=author)
    page_obj = pagination(posts, request, POST_ON_PAGE)
    following = author.following.exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Вывод на страницу подробной информации о посте"""
    template = 'posts/post_detail.html'
    form = CommentForm()
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Создание записи/поста"""
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    context = {
        'form': form,
    }
    if request.method == 'GET':
        return render(request, template, context)
    if request.method == 'POST':
        if not form.is_valid():
            return render(request, template, context)
        post = form.save(commit=False)
        post.author = request.user
        post.save()
    return redirect('posts:profile', username=post.author)


@login_required
def post_edit(request, post_id):
    """Редактирование выбранной записи/поста"""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    if post.author == request.user:
        if request.method == 'POST':
            if not form.is_valid():
                return render(request, template, context)
            form.save()
        if request.method == 'GET':
            return render(request, template, context)
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    """Добавление комментария к посту"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Вывод на страницу постов авторов, на которых подписан пользователь"""
    template = 'posts/follow.html'
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(post_list, request, POST_ON_PAGE)
    context = {
        "page_obj": page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписка на автора"""
    author = get_object_or_404(User, username=username)
    if author != request.user and not author.following.exists():
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Отписка от автора"""
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:follow_index')
