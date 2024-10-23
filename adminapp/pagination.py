from rest_framework.pagination import PageNumberPagination


class CustomerViewPagination(PageNumberPagination):
    page_size = 2      # Default items per page
    page_size_query_param = 'page_size'     # Allow the user to change the number of items per page
    max_page_size = 100     # Maximum limit for page size