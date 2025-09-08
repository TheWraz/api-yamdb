"""Команда импорта категорий, жанров, произведений и связей из CSV."""

from csv import DictReader
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand

from api.models import Category, Genre, Title, GenreTitle


class Command(BaseCommand):
    """Импортирует данные из static/data/*.csv в соответствующие модели."""

    help = 'Импорт категорий, жанров, произведений и связей title↔genre из CSV.'

    def handle(self, *args, **kwargs):
        data_dir = Path(settings.BASE_DIR) / 'static' / 'data'

        self._load_categories(data_dir / 'category.csv')
        self._load_genres(data_dir / 'genre.csv')
        self._load_titles(data_dir / 'titles.csv')
        self._load_genre_title(data_dir / 'genre_title.csv')

        self.stdout.write(self.style.SUCCESS('Импорт завершён.'))

    def _load_categories(self, path):
        """Импорт категорий из category.csv (id,name,slug)."""

        if not path.exists():
            self.stdout.write(self.style.WARNING(f'Файл не найден: {path.name}'))
            return
        created = 0
        with path.open(encoding='utf-8') as f:
            for row in DictReader(f):
                _, was_created = Category.objects.get_or_create(
                    id=int(row['id']),
                    defaults={'name': row['name'].strip(), 'slug': row['slug'].strip()},
                )
                created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f'Категории: добавлено {created}.'))

    def _load_genres(self, path):
        """Импорт жанров из genre.csv (id,name,slug)."""

        if not path.exists():
            self.stdout.write(self.style.WARNING(f'Файл не найден: {path.name}'))
            return
        created = 0
        with path.open(encoding='utf-8') as f:
            for row in DictReader(f):
                _, was_created = Genre.objects.get_or_create(
                    id=int(row['id']),
                    defaults={'name': row['name'].strip(), 'slug': row['slug'].strip()},
                )
                created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f'Жанры: добавлено {created}.'))

    def _load_titles(self, path):
        """Импорт произведений из titles.csv (id,name,year,category)."""

        if not path.exists():
            self.stdout.write(self.style.WARNING(f'Файл не найден: {path.name}'))
            return
        created = 0
        with path.open(encoding='utf-8') as f:
            for row in DictReader(f):
                category = Category.objects.get(id=int(row['category'])) if row['category'] else None
                _, was_created = Title.objects.get_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'].strip(),
                        'year': int(row['year']) if row['year'] else None,
                        'category': category,
                    },
                )
                created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f'Произведения: добавлено {created}.'))

    def _load_genre_title(self, path):
        """Импорт связей из genre_title.csv (id, title_id, genre_id)."""

        if not path.exists():
            self.stdout.write(self.style.WARNING(f'Файл не найден: {path.name}'))
            return
        created = 0
        with path.open(encoding='utf-8') as f:
            for row in DictReader(f):
                title = Title.objects.get(id=int(row['title_id']))
                genre = Genre.objects.get(id=int(row['genre_id']))
                _, was_created = GenreTitle.objects.get_or_create(title=title, genre=genre)
                created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f'Связи жанров/произведений: добавлено {created}.'))
