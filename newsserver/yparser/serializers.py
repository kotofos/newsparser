from rest_framework import serializers
from yparser.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField()
    class Meta:
        model = Article
        fields = ['id', 'title', 'url', 'created']
