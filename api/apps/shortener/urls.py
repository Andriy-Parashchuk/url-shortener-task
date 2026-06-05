from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShortURLViewSet

router = DefaultRouter()
router.register(r'', ShortURLViewSet, basename='shorturl')

urlpatterns = [
    path('', include(router.urls)),
]
