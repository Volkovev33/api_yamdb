from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


ROLES = [
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор')
]


class User(AbstractUser):
    bio = models.TextField('Биография', blank=True)
    email_code = models.IntegerField('Код подтверждения', default=00000)
    role = models.CharField(
        'Роль', max_length=150, default='user', choices=ROLES
    )

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=255)
    year = models.IntegerField()
    description = models.TextField(
        blank=True,
        null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles_in_category')
    genre = models.ManyToManyField(Genre)

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField('Отзыв')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='review',
        null=True
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1,
                              message='Упс, оценка ниже допустимой'),
            MaxValueValidator(10,
                              message='Упс, оценка выше допустимой'),
        ]
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'


class Comment(models.Model):
    text = models.TextField('Комментарии')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
