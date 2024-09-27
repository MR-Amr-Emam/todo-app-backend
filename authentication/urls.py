from django.urls import path

from .apis import CreateUserApi, PerformUserApi, LogoutApi, GetTokenPairApi, RefreshTokenApi, PerformProfileImage



urlpatterns = [
    path('create', CreateUserApi.as_view()),
    path('perform_user', PerformUserApi.as_view()),
    path('logout', LogoutApi.as_view()),
    path('token', GetTokenPairApi.as_view()),
    path('token/refresh', RefreshTokenApi.as_view()),
    path('perform_profile_image', PerformProfileImage.as_view()),
]
