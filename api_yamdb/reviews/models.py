from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin'
        MODERATOR = 'moderator'
        USER = 'user'

    bio = models.TextField('Биография', blank=True)
    confirmation_code = models.CharField(
        'Код подтверждения', default="", max_length=64
    )
    role = models.CharField(
        'Роль', max_length=20, default=Role.USER, choices=Role.choices
    )
    REQUIRED_FIELDS = ["email"]

    @property
    def is_moderator_role(self):
        return self.role == self.Role.MODERATOR

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Название', max_length=255)
    year = models.PositiveSmallIntegerField('Год выхода')
    description = models.TextField('Описание', blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles_in_category', null=True,
        verbose_name='Категория')
    genre = models.ManyToManyField(
        Genre, through='GenreTitle',
        verbose_name='Жанр')

    class Meta:
        ordering = ('name',)
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField('Отзыв')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(
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
        unique_together = [['author', 'title']]
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'


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
        verbose_name_plural = 'Комментарии'


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
