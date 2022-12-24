from django.contrib.auth import views
from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from .views import SignUp


app_name = 'users'

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path(
        'login/',
        views.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'logout/',
        views.LogoutView.as_view(
            template_name='users/logged_out.html',
        ),
        name='logout'
    ),
    path('password_change/', views.PasswordChangeView.as_view
         (template_name='users/password_change_form.html'),
         name='password_change_form'),
    path('password_change/done/', views.PasswordChangeDoneView.as_view
         (template_name='users/password_change_done.html'),
         name='password_change_done'),
    path('password_reset/', views.PasswordResetView.as_view
         (template_name='users/password_reset_form.html',
          email_template_name='users/password_reset_email.html',
          success_url=reverse_lazy('users:password_reset_done')),
         name='password_reset_form'),
    path('password_reset/done/',
         login_required(views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html',
         )),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view
         (template_name='users/password_reset_confirm.html',
          success_url=reverse_lazy('users:password_reset_complete')),
         name='password_reset_confirm'),
    path('password_reset/complete/',
         login_required(views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html',
         )),
         name='password_reset_complete'),
]
