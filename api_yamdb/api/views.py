from random import randint

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins

from rest_framework import viewsets, views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title, Review, User, Comment
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrModeratorOrAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleSerializer, UserSerializer, TokenSerializer)


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().order_by('id')
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Review."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrModeratorOrAdminOrReadOnly,]

    def get_title(self):
        """Объект текущего произведения."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        """Queryset c отзывами."""
        return self.get_title().review.all()

    def perform_create(self, serializer):
        """Создает отзыв для произведения."""
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для объектов модели Comment."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrModeratorOrAdminOrReadOnly,]

    def get_review(self):
        """Возвращает объект текущего отзыва."""
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        """Queryset c комментариями для текущего review."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Создает комментарий для текущего review."""
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('=username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_object(self):
        if self.kwargs['username'] == 'me':
            return self.request.user
        else:
            return super().get_object()

    def destroy(self, request, *args, **kwargs):
        if self.kwargs['username'] == 'me':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(self, request, *args, **kwargs)

    def perform_update(self, serializer):
        if self.kwargs['username'] == 'me':
            serializer.save(role=self.request.user.role)
        else:
            serializer.save()

    def get_permissions(self):
        if 'username' in self.kwargs and self.kwargs['username'] == 'me':
            if self.request.method in ('PATCH', 'GET'):
                self.permission_classes = [IsAuthenticated, ]
        else:
            self.permission_classes = [IsAdmin, ]
        return super(UserViewSet, self).get_permissions()


class RegistrationView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        confirmation_code = randint(10000, 99999)

        if User.objects.filter(username=username, email=email).exists():
            return Response(status=status.HTTP_200_OK)
        if username == 'me':
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(confirmation_code=confirmation_code)

            send_mail(
                subject='API YaMDB, регистрация',
                message=f'Ваш код подтверждения {confirmation_code}',
                from_email='Practicum15@yandex.ru',
                recipient_list=(f'{email}',),
                fail_silently=False,
            )
            return Response(request.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_object_or_404(User, username=data.get('username'))
        if user.confirmation_code == data.get('confirmation_code'):
            refresh = RefreshToken.for_user(user)
            token = {'token': str(refresh.access_token)}
            return Response(token, status=status.HTTP_200_OK)
        return Response(
            {'confirmation_code': 'Не верный код'},
            status=status.HTTP_400_BAD_REQUEST)
