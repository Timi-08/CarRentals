from django.apps import apps
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Welcome to FAST CARS! Your account has been created.')
        return redirect('home')
    return render(request, 'accounts/form.html',
                  {'form': form, 'title': 'Create an account', 'button': 'Register'})


@require_POST
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


@login_required
def profile_edit(request):
    u_form = UserUpdateForm(request.POST or None, instance=request.user)
    p_form = ProfileUpdateForm(request.POST or None, instance=request.user.profile)
    if request.method == 'POST' and u_form.is_valid() and p_form.is_valid():
        u_form.save()
        p_form.save()
        messages.success(request, 'Profile updated.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile_edit.html', {'u_form': u_form, 'p_form': p_form})


def admin_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user.is_staff:
            login(request, user)
            return redirect('accounts:admin_dashboard')
        form.add_error(None, 'This account does not have administrator access.')
    return render(request, 'accounts/form.html',
                  {'form': form, 'title': 'Admin login', 'button': 'Log in'})


@require_POST
def admin_logout(request):
    logout(request)
    return redirect('accounts:admin_login')


def _count(app_label, model_name):
    """Safe count: returns 0 until the teammate's model exists."""
    try:
        return apps.get_model(app_label, model_name).objects.count()
    except LookupError:
        return 0


@staff_member_required(login_url='accounts:admin_login')
def admin_dashboard(request):
    context = {
        'users_count': User.objects.filter(is_staff=False).count(),
        'bookings_count': _count('bookings', 'Booking'),
        'subscribers_count': _count('contact', 'Subscriber'),
        'queries_count': _count('contact', 'Contact'),   # rename to match Isreal's model
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@staff_member_required(login_url='accounts:admin_login')
def admin_user_list(request):
    users = User.objects.filter(is_staff=False).select_related('profile').order_by('-date_joined')
    page = Paginator(users, 10).get_page(request.GET.get('page'))
    return render(request, 'accounts/admin_user_list.html', {'page_obj': page})