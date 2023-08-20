import csv

from django.core.management import BaseCommand
from django.conf import settings

from reviews.models import (Category, Genre, GenreTitle,
                            Title, Comment, Review, User)

# файлы должны импортироваться в определённом порядке,
# чтобы для полей FOREIGN KEY уже существовали значения в др. таблицах
MODEL_FILE_MAPPING = {
    User: 'users.csv',
    Category: 'category.csv',
    Title: 'titles.csv',  # тут косячное поле category
    Review: 'review.csv',  # тут косячное поле author
    Comment: 'comments.csv',  # тут косячное поле author
    Genre: 'genre.csv',
    GenreTitle: 'genre_title.csv'
}


def replace_wrong_fields(model, fieldnames_list):
    for name in fieldnames_list:
        type = model._meta.get_field(name).get_internal_type()
        if type == 'ForeignKey' and not name.endswith('_id'):
            fieldnames_list = [
                element.replace(name, name + '_id')
                for element in fieldnames_list
            ]
    return fieldnames_list


class Command(BaseCommand):

    def handle(self, *args, **options):
        folder_path = str(settings.BASE_DIR) + '\\static\\data\\'
        for model, file_name in MODEL_FILE_MAPPING.items():
            file_path = folder_path + file_name
            with open(file_path,
                      newline='',
                      encoding='utf-8') as file:
                data = csv.DictReader(file)
                data.fieldnames = replace_wrong_fields(model, data.fieldnames)
                values = [
                    model(**row)
                    for row in data
                ]
                model.objects.all().delete()
                model.objects.bulk_create(values)
                self.stdout.write(self.style.SUCCESS(f'{file_name} is loaded'))
