from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Show the profile form inline on the Django admin user screen.
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

# Extend the default user admin so staff can manage profile fields without leaving the user screen.
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)