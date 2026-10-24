from django.conf import settings
from django.db import models

# Extra account details that extend the default Django user with contact info.
class Profile(models.Model):
    # One profile belongs to exactly one user and is accessed through the related name.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"