from rest_framework import generics, filters
from rest_framework.exceptions import APIException
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from yparser.models import Article
from yparser.serializers import ArticleSerializer


class InvalidArgument(APIException):
    status_code = 400
    default_detail = 'Invalid input.'
    default_code = 'invalid'


class BareResultLimitOffsetPagination(LimitOffsetPagination):
    # value to prevent int overflow in database
    # todo move to settings.py
    MAX_INT = 9223372036854775807

    def get_paginated_response(self, data):
        """Return only data"""
        return Response(data)

    def get_limit(self, request):
        limit = super().get_limit(request)
        if limit > self.MAX_INT:
            raise InvalidArgument('limit is too large')
        return limit

    def get_offset(self, request):
        offset = super().get_offset(request)
        if offset > self.MAX_INT:
            raise InvalidArgument('offset is too large')
        return offset


class ArticleList(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    pagination_class = BareResultLimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'
    ordering = ['id']
