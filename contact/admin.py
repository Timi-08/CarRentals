from django.contrib import admin

from .models import Contact, ContactDetails, PageContent, Subscriber


# Contact form submissions are read-only for staff; they are customer messages, not admin-created records.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'body')


# Keep only one editable ContactDetails row so the contact page stays consistent.
@admin.register(ContactDetails)
class ContactDetailsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'phone', 'email')

    def has_add_permission(self, request):
        return not ContactDetails.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
