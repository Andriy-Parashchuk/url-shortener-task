from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, CharField


class RegisterSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password")
