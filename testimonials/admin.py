from django.contrib import admin
from .models import Testimonial


# Admin controls for approving or hiding customer reviews.
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_message', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'message')
    actions = ['activate', 'deactivate']

    def short_message(self, obj):
        return obj.message[:50]

    @admin.action(description="Activate selected testimonials")
    def activate(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected testimonials")
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)