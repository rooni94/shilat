from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import me

urlpatterns = [
    path("token/", obtain_auth_token),
    path("me/", me),
]
