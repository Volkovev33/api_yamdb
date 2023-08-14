from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, views, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from reviews.models import Title, Review

from .permissions import AuthorOrRead
from .serializers import CommentSerializer, ReviewSerializer, UserSerializer

User = get_user_model()

class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Review."""

    serializer_class = ReviewSerializer
    permission_classes = (
        AuthorOrRead
    )

    def get_title(self):
        """Объект текущего произведения."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        """Queryset c отзывами."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Создает отзыв для произведения."""
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели Comment."""

    serializer_class = CommentSerializer
    permission_classes = (
        AuthorOrRead
    )

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
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegistrationView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.save()['email_code']
            email = request.data.get('email')
            send_mail(
                subject='API YaMDB, регистрация',
                message=f'Ваш код подтверждения {code}',
                from_email='Practicum15@yandex.ru',
                recipient_list=f'{email}',
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
