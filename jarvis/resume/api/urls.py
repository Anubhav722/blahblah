from django.conf.urls import url
from jarvis.resume.views import (
    ResumeDetailView, Resume, SkillsSuggestion, TrialUserView,
    TrialResumeDetailView, SampleResumeDetailView, SampleResumeView,
    ValidateTrialUser, GetUploadLimitView, ResumeParseInternal, ResumeFilter,
    ResumeSyncView, ResumeFilterDetailView, TopCompaniesList, AcademicDegreeList,
    ResumeBasicDetailsView
)
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='ResumeParser API')

urlpatterns = [
    url(r'^$', Resume.as_view()),
    url(r'^docs/?$', schema_view, name="api_docs"),
    url(r'^filter/?$', ResumeFilter.as_view()),
    url(r'^filter/(?P<id>[0-9a-z-]+)/?$', ResumeFilterDetailView.as_view()),
    url(r'^limit/?$', GetUploadLimitView.as_view(), name='get_upload_limit'),
    url(r'^sync', ResumeSyncView.as_view()),
    url(r'^companies/top/?$', TopCompaniesList.as_view()),
    url(r'^degrees/?$', AcademicDegreeList.as_view()),
    url(r'^basic-details/$', ResumeBasicDetailsView.as_view()),
    url(
        r'^internal/?$',
        ResumeParseInternal.as_view(),
        name='resume_parse_internal'
    ),
    url(
        r'^sample/?$',
        SampleResumeView.as_view(),
        name='try_sample_resume'
    ),
    url(
        r'^sample/(?P<id>[0-9a-z-]+)/?$',
        SampleResumeDetailView.as_view(),
        name='sample_resume_details'
    ),
    url(r'^trial/?$', TrialUserView.as_view(), name='upload_trial_resume'),
    url(
        r'^trial/(?P<id>[0-9a-z-]+)/?$',
        TrialResumeDetailView.as_view(),
        name='trial_resume_details'
    ),
    url(
        r'^trial-user/validate/$',
        ValidateTrialUser.as_view(),
        name='validate_trial_user'
    ),
    url(r'^skill-suggestion/$', SkillsSuggestion.as_view(), name='skills_suggestion'),
    url(r'^(?P<id>[0-9a-z-]+)', ResumeDetailView.as_view(), name='resume_details'),
]
