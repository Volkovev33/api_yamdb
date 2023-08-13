from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import CategoryViewSet, TitleViewSet, GenreViewSet


router = SimpleRouter()
router.register('categories', CategoryViewSet)
router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)


urlpatterns = [
    path('v1/', include(router.urls)),
]