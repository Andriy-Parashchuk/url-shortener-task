from django.db.models import Count
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import ShortURL
from .serializer import ShortURLSerializer, ClickEventSerializer


class ShortURLViewSet(ModelViewSet):
    serializer_class = ShortURLSerializer

    def get_queryset(self):
        return ShortURL.objects.filter(owner=self.request.user).annotate(click_count=Count('clicks'))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

