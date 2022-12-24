from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment
from .utils import paginate_page


def index(request):
    posts = Post.objects.select_related('author', 'group')
    page_obj = paginate_page(request, posts)
    return render(request, 'posts/index.html', {
        'page_obj': page_obj,
    })


def group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts = group.posts.select_related('author')
    page_obj = paginate_page(request, group_posts)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'posts': group_posts,
        'page_obj': page_obj,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group')
    page_obj = paginate_page(request, post_list)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('group'), id=post_id)
    comments = post.comments.select_related('post')  # Правильно?
    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm(),
    }
    return render(request, 'posts/post_details.html', context)


@login_required
def post_create(request):
    post = Post.objects.select_related('author')
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post_item = form.save(commit=False)
        post_item.author = request.user
        post_item.save()
        return redirect('posts:profile', post_item.author)

    return render(
        request,
        'posts/create_post.html',
        {'post': post, 'form': form}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        messages.error(request, 'Вы не можете редактировать чужие публикации!')
        return redirect('posts:post_details', post_id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_details', post_id)
    return render(
        request,
        'posts/create_post.html',
        {'post': post, 'form': form, 'is_edit': True},
    )


@login_required
def post_delete(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user == post.author:
        post.delete()
        return redirect('posts:index')
    messages.error(request, 'Вы не можете удалять чужие публикации!')
    return redirect('posts:post_details', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post.objects.select_related('group'), id=post_id)
    comments = post.comments.select_related('author')  # Правильно?
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_details', post_id)
    # Без добавления render при ошибке валидации формы не показывает
    # пользователю ValidationError. Может есть и другой способ выводить их,
    # например через messages, но я сделал как в PostForm. В коде от теории,
    # как обычно, view выглядит по-другому, пришлось писать свою.
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_details.html', context)
