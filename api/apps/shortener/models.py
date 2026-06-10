import secrets

from django.db import models


class ShortURL(models.Model):
    original_url = models.URLField()
    short_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.original_url} -> {self.short_code}"

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_short_code()
        super().save(*args, **kwargs)

    @classmethod
    def generate_short_code(cls):
        while True:
            short_code = secrets.token_urlsafe(6)
            if not cls.objects.filter(short_code=short_code).exists():
                return short_code


class ClickEvent(models.Model):
    short_url = models.ForeignKey(ShortURL, related_name='clicks', on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    browser = models.CharField(max_length=50)
    os = models.CharField(max_length=50)
    device_type = models.CharField(max_length=50)

    def __str__(self):
        return f"Click on {self.short_url.short_code} at {self.clicked_at}"

    class Meta:
        indexes = [
            models.Index(
                fields=["short_url", "clicked_at"]
            )
        ]
