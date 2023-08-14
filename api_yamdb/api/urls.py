from django.urls import path, include
from rest_framework import routers

from .views import UserViewSet

router = routers.DefaultRouter()
# router.register(r'users', UserViewSet, basename='User')
router.register(r'auth/signup', UserViewSet, basename='signup')

urlpatterns = [
    path('v1/', include(router.urls)),
]
