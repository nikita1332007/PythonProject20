from django.urls import path

from mailing_app.views import ProfileView
from .views import RegisterView, ActivateAccountView, UsersListView, UserBlockToggleView
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),

    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),

    path('users/', UsersListView.as_view(), name='users-list'),
    path('users/<int:pk>/block-toggle/', UserBlockToggleView.as_view(), name='user-block-toggle'),
    path('profile/', ProfileView.as_view(), name='profile'),
]