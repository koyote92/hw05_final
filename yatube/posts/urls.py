from django.urls import path

from . import views


app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group, name='group'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_details'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_update'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/comment/<int:comment_id>/delete/',
         views.delete_comment, name='comment_delete'),
]
