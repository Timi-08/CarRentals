from django.conf import settings
from django.db import models


class Contact(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in_progress', 'In progress'
        RESOLVED = 'resolved', 'Resolved'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='contact_messages',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'contact query'
        verbose_name_plural = 'contact queries'

    def __str__(self):
        return f'{self.subject} ({self.email})'


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-subscribed_at',)

    def __str__(self):
        return self.email


class SiteContent(models.Model):
    homepage_title = models.CharField(max_length=150, default='FAST CARS')
    homepage_intro = models.TextField(
        blank=True, default='Find the right car for your next journey.'
    )
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_address = models.CharField(max_length=255, blank=True)
    class Meta:
        verbose_name = 'site content and contact detail'
        verbose_name_plural = 'site content and contact details'

    def __str__(self):
        return 'Site content and contact details'

    @classmethod
    def get_solo(cls):
        content, _ = cls.objects.get_or_create(pk=1)
        return content
