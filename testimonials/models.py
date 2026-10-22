from django.conf import settings
from django.db import models


class Testimonial(models.Model):
    """A customer review. Hidden until an admin activates it (TST-03)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='testimonials')
    message = models.TextField(max_length=1000)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:40]}"