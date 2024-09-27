from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.functional import SimpleLazyObject
from django.http import HttpRequest
from django.http.response import HttpResponseBase
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions
from django.conf import settings
from django.middleware import csrf
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.settings import api_settings

def profile_image_storage(instance, file_name):
    return f"{instance.username}/profile/profile_image.jpg"

class User(AbstractUser):
    profile_image = models.ImageField(upload_to=profile_image_storage, default="default/profile-image.jpg")
    timezone = models.CharField(max_length=150)


def enforce_csrf(request):
    check = CSRFCheck(request)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)


class CookiesJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token: bytes) -> Token:
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except:
                return None
        raise exceptions.NotAcceptable()

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        enforce_csrf(request)
        if(validated_token is None):
            return None
        return self.get_user(validated_token), validated_token

class CookiesCsrfViewMiddleware(csrf.CsrfViewMiddleware):
    def process_response(self, request: HttpRequest, response: HttpResponseBase) -> HttpResponseBase:
        csrf.get_token(request)
        return super().process_response(request, response)


class CookiesAuthentication:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        if raw_token is None:
            return self.get_response(request)
        validated_token = self.get_validated_token(raw_token)
        enforce_csrf(request)
        if(validated_token is None):
            return self.get_response(request)
        user_id = validated_token.get("user_id")
        request.user = User.objects.get(id=user_id)
        return self.get_response(request)
    
    def get_validated_token(self, raw_token: bytes) -> Token:
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except:
                return None
        raise exceptions.NotAcceptable()