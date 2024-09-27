from django.contrib.auth import authenticate
from django.conf import settings
from django.views import View
from django.http import HttpResponse
from os.path import join

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.exceptions import NotAcceptable, NotAuthenticated

from .models import User
from .serializers import CreateUserSerializer, UserSerializer


def set_cookies(response, refresh):
    response.set_cookie(
        key = settings.SIMPLE_JWT["AUTH_COOKIE"],
        value = str(refresh.access_token),
        domain = settings.ALLOWED_HOSTS[0],
        expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        httponly=True,
        secure=False,
        samesite="Lax",
    )
    response.set_cookie(
        key = settings.SIMPLE_JWT["REFRESH_COOKIE"],
        value = str(refresh),
        path = "/authentication/token/refresh",
        domain = settings.ALLOWED_HOSTS[0],
        expires = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        httponly=True,
        secure=False,
        samesite="Lax",
    )
    return response


class CreateUserApi(CreateAPIView):
    serializer_class = CreateUserSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        user = serializer.create(serializer.validated_data)
        response = Response()
        response.data = serializer.data
        refresh = RefreshToken.for_user(user)
        set_cookies(response, refresh)
        return response


class PerformUserApi(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user

class LogoutApi(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        response = Response()
        response.delete_cookie(
            key = settings.SIMPLE_JWT["AUTH_COOKIE"],
            path = "/",
            domain = settings.ALLOWED_HOSTS[0],
        )
        response.delete_cookie(
            key = "csrftoken",
            path = "/",
            domain = settings.ALLOWED_HOSTS[0],
        )
        response.delete_cookie(
            key = settings.SIMPLE_JWT["REFRESH_COOKIE"],
            path = "/authentication/token/refresh",
            domain = settings.ALLOWED_HOSTS[0],
        )
        return response

class GetTokenPairApi(APIView):
    serializer_class = UserSerializer
    def post(self, request):
        request = request.data
        user = authenticate(username=request["username"], password=request["password"])
        if(user is None):
            raise NotAcceptable()
        response = Response()
        serializer = self.serializer_class(user)
        response.data = serializer.data
        refresh = RefreshToken.for_user(user)
        set_cookies(response, refresh)
        return response

class RefreshTokenApi(APIView):
    def post(self, request):
        refresh_token = RefreshToken(request.COOKIES.get(settings.SIMPLE_JWT["REFRESH_COOKIE"]))
        id=refresh_token.payload.get("user_id", None)
        if(id==None):
            raise NotAuthenticated()
        user = User.objects.get(id=id)
        refresh = RefreshToken.for_user(user)
        response = Response()
        set_cookies(response, refresh)
        return response


class PerformProfileImage(View):
    def get(self, request):
        if(not request.user.is_authenticated):
            return HttpResponse(b"{'error':'not authorized'}", content_type="application/json", status=401)
        image = request.user.profile_image
        with open(image.path, "rb") as image:
            image = image.read()
            response_image = HttpResponse(content=image, content_type="image/jpg")
            return response_image

    def post(self, request):
        if(not request.user.is_authenticated):
            return HttpResponse(b"{'error':'not authorized'}", content_type="application/json", status=401)
        image = request.FILES["profile_image"]
        if request.user.profile_image.path!=join(settings.BASE_DIR, "media\default\profile-image.jpg"):
            request.user.profile_image.delete()
        request.user.profile_image = image
        request.user.save()
        image_url = settings.DOMAIN_ORIGIN + "/authentication/perform_profile_image"
        content = '{"profile_image":"' + image_url + '"}'
        return HttpResponse(content=content.encode(), content_type="application/json")


