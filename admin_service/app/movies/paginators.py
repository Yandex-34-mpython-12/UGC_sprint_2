from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('prev', self.get_previous_number()),
            ('next', self.get_next_number()),
            ('results', data)
        ]))

    def get_next_number(self):
        if not self.page.has_next():
            return None
        return self.page.next_page_number()

    def get_previous_number(self):
        if not self.page.has_previous():
            return None
        return self.page.previous_page_number()
