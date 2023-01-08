import csv

from django.core.management import BaseCommand

from posts.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка из csv файла'

    def handle(self, *args, **kwargs):
        path = r'D:\Dev\foodgram-project-react\data'
        with open(
            f'{path}/ingredients.csv',
            'r',
            encoding='utf-8'
        ) as csv_file:
            reader = csv.DictReader(csv_file)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in reader)
        self.stdout.write(
            self.style.SUCCESS('Все данные залиты в базу данных')
        )
