from typing import Dict, Iterable

import requests
from bs4 import BeautifulSoup
from django.db import models, IntegrityError

SOURCE_URL = 'https://news.ycombinator.com/'


class Article(models.Model):
    DOWNLOAD_MAX_COUNT = 30
    url = models.URLField(max_length=512, unique=True)
    title = models.CharField(max_length=512)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def download_articles(cls) -> int:
        res = cls.scrap_articles()
        return cls.save_articles(res)

    @classmethod
    def scrap_articles(cls) -> Iterable[Dict]:
        r = requests.get('https://news.ycombinator.com/')
        html_doc = r.text

        soup = BeautifulSoup(html_doc, 'html.parser')
        res = soup.find_all('a', class_='storylink')

        return (
            {'url': a_tag['href'], 'title': a_tag.text} for a_tag in
            res[:cls.DOWNLOAD_MAX_COUNT]
        )

    @classmethod
    def save_articles(cls, parsed_articles: Iterable[Dict]) -> int:
        count = 0
        for article_item in parsed_articles:
            article = Article(
                url=article_item['url'],
                title=article_item['title']
            )
            try:
                article.save()
                count += 1
            except IntegrityError:
                pass

        return count
