from django.shortcuts import get_object_or_404

from rest_framework import viewsets

from reviews.models import Title, Review

from .permissions import AuthorOrRead
from .serializers import CommentSerializer, ReviewSerializer


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
