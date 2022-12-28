from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib import messages

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow
from .utils import paginate_page


# Я тоже сюда сначала добавил кэширование, а потом в теории сказали "в этом
# проекте пихайте в шаблон".
@cache_page(20)
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
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'following': following,
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
        return redirect('posts:profile', post_item.author.username)

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


# Этой вью нет в спринте, сделана для себя.
@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post.objects.select_related('group'), id=post_id)
    if request.user == post.author:
        post.delete()
        return redirect('posts:index')
    messages.error(request, 'Вы не можете удалять чужие публикации!')
    return redirect('posts:post_details', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id)
    comments = post.comments.select_related('post')  # Правильно? Или 404?
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_details', post_id)
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_details.html', context)


# Этой вью нет в спринте, сделана для себя.
@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id)
    comment = get_object_or_404(post.comments.select_related('post'),
                                id=comment_id)
    if request.user == comment.author:
        comment.delete()
        return redirect('posts:post_details', post_id)
    messages.error(request, 'Вы не можете удалять чужие комментарии!')
    return redirect('posts:post_details', post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginate_page(request, posts)
    return render(request, 'posts/follow.html', {'page_obj': page_obj})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    if follower.exists():
        follower.delete()
    return redirect('posts:profile', username=author)
