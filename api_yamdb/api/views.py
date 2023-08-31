from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets, views, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title, Review, User, Comment
from api.filters import TitleFilter
from api.permissions import (IsAdmin, ReadOnly,
                             IsAuthorOrModeratorOrAdminOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleGetSerializer, TitleCreateSerializer,
                             UserSerializer, TokenSerializer)

ALLOWED_METHODS = ['get', 'post', 'patch', 'delete']


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = ((IsAdmin|ReadOnly),)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('review__score')
    ).order_by('id')
    permission_classes = ((IsAdmin|ReadOnly),)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ALLOWED_METHODS

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleGetSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    http_method_names = ALLOWED_METHODS

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        return self.get_title().review.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    http_method_names = ALLOWED_METHODS

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('=username',)
    lookup_field = 'username'
    http_method_names = ALLOWED_METHODS

    @action(detail=False, methods=['GET', 'PATCH'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        self.kwargs['username'] = request.user.username
        if request.method == 'GET':
            return self.retrieve(request)
        elif request.method == 'PATCH':
            return self.partial_update(request)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def perform_update(self, serializer):
        serializer.save(role=self.request.user.role)


class RegistrationView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        if User.objects.filter(username=request.data.get('username'),
                               email=request.data.get('email')).exists():
            return Response(data=request.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = get_object_or_404(
            User, username=serializer.validated_data.get('username')
        )
        confirmation_code = default_token_generator.make_token(user)

        send_mail(
            subject='API YaMDB, регистрация',
            message=f'Ваш код подтверждения {confirmation_code}',
            from_email='Practicum15@yandex.ru',
            recipient_list=(serializer.validated_data.get('email'),),
            fail_silently=False,
        )
        return Response(request.data, status=status.HTTP_200_OK)


class TokenView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_object_or_404(User, username=data.get('username'))
        confirmation_code = data.get('confirmation_code')
        if default_token_generator.check_token(user=user,
                                               token=confirmation_code):
            refresh = RefreshToken.for_user(user)
            token = {'token': str(refresh.access_token)}
            return Response(token, status=status.HTTP_200_OK)
        return Response(
            {'confirmation_code': 'Не верный код'},
            status=status.HTTP_400_BAD_REQUEST)
