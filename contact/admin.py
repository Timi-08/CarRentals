from django.contrib import admin
from .models import Contact, SiteContent, Subscriber


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('user', 'name', 'email', 'subject', 'message', 'created_at')
    ordering = ('-created_at',)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    list_editable = ('is_active',)


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Home page', {'fields': ('homepage_title', 'homepage_intro')}),
        ('Contact details', {'fields': ('contact_email', 'contact_phone', 'contact_address')}),
    )

    def has_add_permission(self, request):
        return not SiteContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.pk = 1
        super().save_model(request, obj, form, change)
