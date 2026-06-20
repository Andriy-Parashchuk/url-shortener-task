from django.contrib import admin
from .models import ShortURL, ClickEvent

# Register your models here.
admin.site.register(ShortURL)
admin.site.register(ClickEvent)
