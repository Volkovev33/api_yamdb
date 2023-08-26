import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name='category__slug'
    )
    genre = django_filters.CharFilter(
        field_name='genre__slug'
    )
    year = django_filters.NumberFilter()
    name = django_filters.CharFilter()

    class Meta:
        model = Title
        fields = ('year', 'name', 'category', 'genre', )
