import json
from datetime import timedelta

from django.db.models.functions import TruncDate
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import ShortURL, ClickEvent
from .serializer import ShortURLSerializer, ClickEventSerializer
from .services.redis_service import redis_client
from loguru import logger


class ShortURLViewSet(ModelViewSet):
    serializer_class = ShortURLSerializer

    def get_queryset(self):
        return ShortURL.objects.filter(owner=self.request.user).annotate(click_count=Count('clicks'))

    def retrieve(self, request, *args, **kwargs):
        short_url = self.get_object()
        recent_clicks = ClickEvent.objects.filter(short_url=short_url).order_by('-clicked_at')[:10]
        data = self.get_serializer(short_url).data

        data['recent_clicks'] = ClickEventSerializer(recent_clicks, many=True).data

        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)

        clicks_by_day_qs = (
            ClickEvent.objects
                .filter(short_url_id=pk)
                .filter(clicked_at__date__range=(start_date, end_date))
                .annotate(day=TruncDate('clicked_at'))
                .values('day')
                .annotate(total=Count('id'))
        )

        clicks_map = {c['day']: c['total'] for c in clicks_by_day_qs}

        clicks_by_day = [
            {
                "day": start_date + timedelta(days=i),
                "total": clicks_map.get(start_date + timedelta(days=i), 0)
            }
            for i in range(30)
        ]

        top_browsers = (
            ClickEvent.objects
                .filter(short_url_id=pk)
                .values('browser')
                .annotate(total=Count('id'))
                .order_by('-total')[:5]
        )

        top_os = (
            ClickEvent.objects
                .filter(short_url_id=pk)
                .values('os')
                .annotate(total=Count('id'))
                .order_by('-total')[:5]
        )

        return Response({
            "click_count": ClickEvent.objects.filter(short_url_id=pk).aggregate(total_clicks=Count('id'))['total_clicks'],
            "clicks_by_day": clicks_by_day,
            "top_browsers": list(top_browsers),
            "top_os": list(top_os),
        })

    @action(detail=False, methods=["get"])
    def summary(self, request):
        urls = ShortURL.objects.filter(owner=request.user)
        total_urls = urls.count()
        total_clicks = urls.aggregate(total_clicks=Count('clicks'))['total_clicks']
        top_urls = (
            urls.annotate(click_count=Count('clicks'))
                .order_by('-click_count')[:5]
        )

        return Response({
            "total_urls": total_urls,
            "total_clicks": total_clicks,
            'top_urls': [
                {
                    "original_url": url.original_url,
                    "short_code": url.short_code,
                    "click_count": url.click_count
                }
                for url in top_urls
            ]

        })


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
