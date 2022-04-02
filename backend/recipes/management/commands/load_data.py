import csv

from django.core.management.base import BaseCommand

from recipes.models import Product


class Command(BaseCommand):
    help = 'Load ingredients data to DB'

    def handle(self, *args, **options):
        with open('../data/ingredients.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            count = 0
            for row in reader:
                name, unit = row
                Product.objects.get_or_create(name=name, measurement_unit=unit)
                count += 1
                if not count % 100:
                    print(f'Обработано: {count} записей.')
