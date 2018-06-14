# DRF Imports
from rest_framework.pagination import LimitOffsetPagination


class ResumeLimitOffsetPagination(LimitOffsetPagination):
    ordering = 'id'
    max_limit = 20
    default_limit = 20
