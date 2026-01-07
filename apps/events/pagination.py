from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class EventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    page_query_param = 'page'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'items': data,
            'total': self.page.paginator.count,
            'page': self.page.number,
            'size': self.page.paginator.per_page
        })
