from .models import ShortURL, ClickEvent
from rest_framework.serializers import ModelSerializer, CharField, IntegerField


class ShortURLSerializer(ModelSerializer):
    click_count = IntegerField(read_only=True)

    class Meta:
        model = ShortURL
        fields = ("id", "original_url", "short_code", "created_at", "click_count")
        read_only_fields = ("short_code", "created_at")


class ClickEventSerializer(ModelSerializer):
    class Meta:
        model = ClickEvent
        fields = ("id", "short_url", "clicked_at", "ip_address", "user_agent", "browser", "os", "device_type")
        read_only_fields = ("short_url", "clicked_at", "ip_address", "user_agent", "browser", "os", "device_type")

