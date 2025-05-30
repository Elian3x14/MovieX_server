from rest_framework.pagination import PageNumberPagination


class MovieReviewPagination(PageNumberPagination):
    page_size = 1  # số review mỗi trang
    page_size_query_param = "page_size"
    max_page_size = 100