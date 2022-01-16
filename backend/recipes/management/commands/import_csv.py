import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag

# Использование:
# 1. отредактировать список app_models, теми файлами, которые надо загрузить.
# Ключ в словаре - имя файла (без разрешения), значение - модель
# 2. имена полей таблиц базы данных и заголовков в csv файле должны точно
# соответстовать
# 3. все поля таблицы базы данных, которые не заполняются из csv должны иметь
# возможность быть пустыми или Null
# 4. запустить файл импорта командой
# python manage.py import_csv [-dd]


class Command(BaseCommand):
    help = 'Загрузка данных в базу'

    def add_arguments(self, parser):
        parser.add_argument(
            '-dd', '--data_dir',
            default=os.path.join(os.path.dirname(settings.BASE_DIR), 'data/'),
            help="Директория начальных данных для загрузки")

    def handle(self, *args, **kwargs):
        data_dir = kwargs['data_dir']

        app_models = {
            'ingredients': Ingredient,
            'tags': Tag,
        }

        for file_name, model in app_models.items():
            with open(
                f'{data_dir}{file_name}.csv', encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(
                    csv_file, delimiter=',', quotechar='"')

                for line in reader:
                    model.objects.create(**line)
            csv_file.close()
            self.stdout.write(
                f'Данные добавлены в таблицу ..._{file_name}')
