from rest_framework.pagination import PageNumberPagination


class SubjectPagination(PageNumberPagination):
    max_page_size = 100
    page_size = 25
    page_size_query_param = 'count'
