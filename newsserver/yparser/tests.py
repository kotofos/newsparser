from django.test import TestCase, TransactionTestCase, Client

from yparser.models import Article


# todo test time. use freezegun
class ArticleSavingTestCase(TestCase):
    def test_articles_scrapped(self):
        res = Article.scrap_articles()
        res = list(res)

        self.assertEqual(len(res), 30)
        self.assertTrue(res[0]['url'])
        self.assertTrue(res[0]['title'])

    def test_one_article__saved(self):
        test_data = [{'title': 'test', 'url': 'test'}]
        Article.save_articles(test_data)

        qs = Article.objects.all()

        res = list(qs)
        article = res[0]
        self.assertEqual(len(qs), 1)
        self.assertEqual(article.url, 'test')
        self.assertEqual(article.title, 'test')

    def test_articles_downloaded_and_saved(self):
        Article.download_articles()

        qs = Article.objects.all()

        res = list(qs)

        self.assertTrue(len(res), 30)
        self.assertTrue(res[0].url)
        self.assertTrue(res[0].title)


class ArticleErrorTestCase(TransactionTestCase):
    def test_non_uique_articles__ignored(self):
        test_data = [
            {'title': 'test', 'url': 'test'},
            {'title': 'test', 'url': 'test'}
        ]

        Article.save_articles(test_data)

        qs = Article.objects.all()

        res = list(qs)
        article = res[0]
        self.assertEqual(len(qs), 1)
        self.assertEqual(article.url, 'test')
        self.assertEqual(article.title, 'test')


class EmptyDbTestCase(TestCase):
    def test_empty_articles__empty_response(self):
        c = Client()
        res = c.get('/posts').json()

        self.assertEqual(len(res), 0)


class ResponseTestCase(TestCase):
    def setUp(self) -> None:
        test_data = [
            {'title': 't1', 'url': 'u1'},
            {'title': 't2', 'url': 'u2'},
            {'title': 't3', 'url': 'u3'},
        ]

        Article.save_articles(test_data)

    def test_articles__returned(self):
        c = Client()
        res = c.get('/posts').json()

        self.assertEqual(len(res), 3)
        self.assertTrue(res[0]['url'])
        self.assertTrue(res[0]['title'])
        self.assertTrue(res[0]['id'])
        self.assertTrue(res[0]['created'])


class OrderingTestCase(TestCase):
    def setUp(self) -> None:
        test_data = [
            {'title': '1', 'url': '3'},
            {'title': '3', 'url': '2'},
            {'title': '2', 'url': '1'},
        ]
        Article.save_articles(test_data)

    def test_ordering__works(self):
        c = Client()
        res = c.get('/posts', {'order': 'title'}).json()

        self.assertEqual(res[0]['title'], '1')
        self.assertEqual(res[1]['title'], '2')
        self.assertEqual(res[2]['title'], '3')

    def test_reversed_ordering__works(self):
        c = Client()
        res = c.get('/posts', {'order': '-title'}).json()

        self.assertEqual(res[0]['title'], '3')
        self.assertEqual(res[1]['title'], '2')
        self.assertEqual(res[2]['title'], '1')

    def test_invalid_ordering__ignored(self):
        c = Client()
        res = c.get('/posts', {'order': 'lol'}).json()

        self.assertEqual(res[0]['title'], '1')
        self.assertEqual(res[1]['title'], '3')
        self.assertEqual(res[2]['title'], '2')


class PaginationTestCase(TestCase):
    def setUp(self):
        test_data = [
            {'title': 't1', 'url': 'u1'},
            {'title': 't2', 'url': 'u2'},
            {'title': 't3', 'url': 'u3'},
        ]

        Article.save_articles(test_data)

    def test_limit_offset__works(self):
        c = Client()
        res = c.get('/posts', {'limit': 1, 'offset': 1, 'order': 'id'}).json()

        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['id'], 2)

    def test_offset_invalid_values__ignored(self):
        c = Client()
        res = c.get('/posts', {'offset': 0, 'limit': 5}).json()
        self.assertEqual(len(res), 3)
        res = c.get('/posts', {'offset': -1, 'limit': 5}).json()
        self.assertEqual(len(res), 3)
        res = c.get('/posts', {'offset': 'NaN', 'limit': 5}).json()
        self.assertEqual(len(res), 3)
        res = c.get('/posts', {'offset': '0,1', 'limit': 5}).json()
        self.assertEqual(len(res), 3)

    def test_limit_invalid_values__ignored(self):
        c = Client()
        res = c.get('/posts', {'limit': 0}).json()
        self.assertEqual(len(res), 3)
        res = c.get('/posts', {'limit': -1}).json()
        self.assertEqual(len(res), 3)
        res = c.get('/posts', {'limit': 'NaN'}).json()
        self.assertEqual(len(res), 3)
        res = c.get('/posts', {'limit': '0,1'}).json()
        self.assertEqual(len(res), 3)

    def test_offset_overflow__bad_request(self):
        c = Client()

        res = c.get('/posts', {'offset': 9999999999999999999})
        self.assertEqual(res.status_code, 400)

    def test_limit_overflow__bad_request(self):
        c = Client()

        res = c.get('/posts', {'limit': 9999999999999999999})
        self.assertEqual(res.status_code, 400)
