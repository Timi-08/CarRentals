from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/form.html',
        redirect_authenticated_user=True,
        extra_context={'title': 'Log in', 'button': 'Log in'}), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('password/change/', login_required(auth_views.PasswordChangeView.as_view(
        template_name='accounts/form.html',
        success_url=reverse_lazy('accounts:profile'),
        extra_context={'title': 'Change password', 'button': 'Update password'})),
        name='password_change'),

    path('password/reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/form.html',
        email_template_name='accounts/password_reset_email.txt',
        success_url=reverse_lazy('accounts:password_reset_done'),
        extra_context={'title': 'Reset your password', 'button': 'Send reset link'}),
        name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/message.html',
        extra_context={'title': 'Check your email',
                        'message': 'We have sent you a link to reset your password.'}),
        name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/form.html',
        success_url=reverse_lazy('accounts:password_reset_complete'),
        extra_context={'title': 'Set a new password', 'button': 'Save password'}),
        name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/message.html',
        extra_context={'title': 'Password changed',
                        'message': 'Your password has been reset. You can now log in.'}),
        name='password_reset_complete'),

    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/password/change/', staff_member_required(
        auth_views.PasswordChangeView.as_view(
            template_name='accounts/form.html',
            success_url=reverse_lazy('accounts:admin_dashboard'),
            extra_context={'title': 'Change admin password', 'button': 'Update password'}),
        login_url='accounts:admin_login'), name='admin_password_change'),
]