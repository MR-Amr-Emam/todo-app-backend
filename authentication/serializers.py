from django.conf import settings

from rest_framework.serializers import ModelSerializer
from .models import User


class CreateUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "timezone", "profile_image"]
        read_only_fields = ["profile_image"]
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        self.instance = user
        return user
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["profile_image"] = settings.DOMAIN_ORIGIN + "/authentication/perform_profile_image"
        return data
    



class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "profile_image", "timezone"]
        read_only_fields = ["profile_image"]
        extra_kwargs = {"username":{"required":False}, "timezone":{"required":False}}
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["profile_image"] = settings.DOMAIN_ORIGIN + "/authentication/perform_profile_image"
        return data

