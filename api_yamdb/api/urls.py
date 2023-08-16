from django.urls import include, path

from rest_framework.routers import SimpleRouter

from api.views import (CategoryViewSet, GenreViewSet, TitleViewSet,
                       RegistrationView, UserViewSet)


router = SimpleRouter()
router.register(r'users', UserViewSet)
router.register('categories', CategoryViewSet)
router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', RegistrationView.as_view(), name='signup')
]
