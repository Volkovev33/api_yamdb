from django.urls import path, include
from rest_framework import routers

from .views import UserViewSet, RegistrationView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', RegistrationView.as_view(), name='signup')
]
