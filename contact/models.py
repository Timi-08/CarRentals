from django.db import models


class Contact(models.Model):
    """A message sent through the Contact Us form (a "contact query")."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'contact query'
        verbose_name_plural = 'contact queries'

    def __str__(self):
        return f'{self.name} <{self.email}>'


class Subscriber(models.Model):
    """An email address subscribed to FAST CARS updates."""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class PageContent(models.Model):
    """Editable text for a static page such as About Us."""
    slug = models.SlugField(unique=True, help_text='Used in the web address, e.g. about-us')
    title = models.CharField(max_length=150)
    body = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'page content'
        verbose_name_plural = 'page content'

    def __str__(self):
        return self.title


class ContactDetails(models.Model):
    """FAST CARS contact details shown on the Contact Us page. Only one row exists."""
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    working_hours = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = 'contact details'
        verbose_name_plural = 'contact details'

    def save(self, *args, **kwargs):
        self.pk = 1  # singleton: there is only ever one row
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'FAST CARS contact details'
