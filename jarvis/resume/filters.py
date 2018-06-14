import django_filters
from .models import Resume

class ResumeFilterSet(django_filters.FilterSet):

    exp_min = django_filters.NumberFilter(name='experience', lookup_expr='gt')
    exp_max = django_filters.NumberFilter(name='experience', lookup_expr='lt')

    loc = django_filters.CharFilter(name='locations__name', lookup_expr='iexact')
    comp = django_filters.CharFilter(method='filter_company')
    inst = django_filters.CharFilter(method='filter_institution')

    code_per = django_filters.CharFilter(method='filter_coding')

    # skill_per = django_filters.CharFilter(method='filter_skills')

    def filter_coding(self, queryset, name, value):
        try:
            value = (float(value) * 5)/100.0
            queryset = queryset.filter(scores__score__gt=value, scores__type=1)
            return queryset
        except TypeError as e:
            return queryset

    def filter_company(self, queryset, name, value):
        if value == 'top':
            queryset = queryset.filter(companies__rank__gt=40)
        return queryset

    def filter_institution(self, queryset, name, value):
        if value == 'top':
            queryset = queryset.filter(companies__score__lt=100)
        return queryset

    class Meta:
        model = Resume
        fields = ('exp_min', 'exp_max', 'code_per')
        strict = django_filters.STRICTNESS.IGNORE
