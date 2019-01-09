from rest_framework import serializers
from .models import Token


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = ('access_token', 'refresh_token')
