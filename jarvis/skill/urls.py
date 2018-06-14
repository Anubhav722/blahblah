from django.conf.urls import url
from .views import (
    RelatedSkills
)

urlpatterns = [
    url(r'^related/?$', RelatedSkills.as_view(), name='related_skills')
]
