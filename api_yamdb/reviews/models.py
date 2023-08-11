from django.db import models


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
    year = models.IntegerField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles_in_category', blank=True, null=True)
    genre = models.ManyToManyField(Genre)

    def __str__(self):
        return self.name
