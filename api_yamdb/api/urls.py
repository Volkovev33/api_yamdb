from django.urls import include, path

from rest_framework.routers import SimpleRouter

from .views import (CategoryViewSet, GenreViewSet, TitleViewSet, RegistrationView,
                    UserViewSet, TokenView, ReviewViewSet, MeViewSet, CommentViewSet)


router = SimpleRouter()
router.register('users', UserViewSet)
router.register(r'users/me', MeViewSet)
router.register('categories', CategoryViewSet)
router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', RegistrationView.as_view(), name='signup'),
    path('v1/auth/token/', TokenView.as_view(), name='token_obtain_pair'),
]
