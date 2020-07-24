from django.core.management.base import BaseCommand, CommandError
from yparser.models import Article


class Command(BaseCommand):
    help = 'Download new articles'

    def handle(self, *args, **options):
        count = Article.download_articles()
        self.stdout.write(
            self.style.SUCCESS(f'Downloaded {count} new articles')
        )
