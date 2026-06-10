import json

from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import ShortURL
from .serializer import ShortURLSerializer, ClickEventSerializer
from .services.redis_service import redis_client
from loguru import logger


class ShortURLViewSet(ModelViewSet):
    serializer_class = ShortURLSerializer

    def get_queryset(self):
        return ShortURL.objects.filter(owner=self.request.user).annotate(click_count=Count('clicks'))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def redirect_view(request, short_code):

    url = get_object_or_404(ShortURL, short_code=short_code)

    event = {
        "short_code": short_code,
        "ip_address": request.META.get(
            "REMOTE_ADDR"
        ),
        "user_agent": request.META.get(
            "HTTP_USER_AGENT"
        ),
    }
    logger.info(
        f"Publishing click for {short_code}"
    )
    logger.info(
        f"Event {event}"
    )
    redis_client.publish(
        "clicks:raw",
        json.dumps(event)
    )

    return redirect(url.original_url)
