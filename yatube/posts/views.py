from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(
        author=profile).order_by("-pub_date").all()
    posts_count = user_posts.count()
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'user_posts': user_posts,
        'posts_count': posts_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    user_posts = Post.objects.filter(author=post_id)
    post_title = post.text[:30]
    context = {
        'post': post,
        'user_posts': user_posts,
        'posts_count': posts_count,
        'post_title': post_title,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    group = Group.objects.all()
    form = PostForm(request.POST)
    if request.method == 'POST' and form.is_valid():
        form = PostForm(request.POST)
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    else:
        form = PostForm()
        context = {
            'form': form,
            'group': group,
        }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    group = Group.objects.all()
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST, instance=post)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'post': post,
        'form': form,
        'group': group,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)
