# Standard library
import os
import json
import uuid
import logging
import itertools
from copy import deepcopy
from uuid import uuid4, UUID

# Third party
from fuzzywuzzy import process
from flanker.addresslib import address
from ratelimit import UNSAFE
from ratelimit.mixins import RatelimitMixin
from django_filters.rest_framework import DjangoFilterBackend

# Django
from api import rest_exceptions
from django.db.models import Q
from django.db import connection
from django.http import Http404
from django.conf import settings
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage, FileSystemStorage

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, throttling
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

# App
import jarvis.resume as resume_app
from jarvis.accounts.models import UserProfile
from jarvis.core.rest.permissions import AllowInternalServiceOnly
from jarvis.resume.models import Resume as ResumeModel
from jarvis.resume.api.pagination import ResumeLimitOffsetPagination
from jarvis.resume.utils.extractor import get_text, get_text_via_ocr
from jarvis.resume.models import Company, Location, Institution
from jarvis.resume.tasks import parse_resume
from jarvis.resume.filters import ResumeFilterSet
from jarvis.resume.common import skill_match_percent
from jarvis.resume.decorators import store_visitor_activity
from forms import UploadFileForm, TrialUseCaseForm, SampleResumeForm, UploadResumeForm
from jarvis.resume.api.serializers import (
    ResumeSerializer, ResumeParseInternalSerializer, ResumeFilterSerializer,
    CompanySerializer,
)
from jarvis.resume.utils.parser_helper import (
    get_sim_hash_for_resume_content, check_hamming_distance,
    disciplines, disciplines_mapping,
)
from jarvis.resume.helpers import (
    support_short_skill_names, get_related_technology_stack, upload_to_s3,
    criteria_to_score, create_resume_instance, get_basics
)
from jarvis.resume.constants import (
    DESPOSABLE_EMAIL_DOMAINS, RESUME_THRESHOLD_COUNT_FOR_TRIAL_VERSION
)

# Global vars
pipe_sep = '|'
logger = logging.getLogger(__file__)


class AcademicDegreeList(APIView):
    def get(self, request, *args, **kwargs):
        resp = []
        for deg in disciplines:
            resp.append({'short_name': deg[0], 'long_name': deg[1]})

        return Response(resp)


class TopCompaniesList(generics.ListAPIView):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.order_by('rank')[:100]


class SkillsSuggestion(APIView):
    authentication_classes = (TokenAuthentication, )

    def get(self, request, *args, **kwargs):
        skill_name = request.query_params.get('q', None)

        if not skill_name:
            # TODO(kaviraj):
            # If no skills matches pass as empty list not empty string.
            # To maintain consistency. Need to check with frontend also to do
            # this cleanup
            logger.debug('Skills not provided against SkillsSuggestion endpoint')
            return Response({'result': ''})

        # TODO(kaviraj):
        # Need to replace with space?. I guess its supposed to be hyphen
        skill_name = skill_name.replace(" ", "").lower()
        result = get_related_technology_stack(skill_name)
        if not result:
            result = support_short_skill_names(skill_name)
        return Response({'result': result})


class ValidateTrialUser(APIView):
    """
    View to validate trial user
    """

    def get(self, request):

        # TODO(kaviraj): Try handling error cases without much exception
        # handling

        try:
            email = request.query_params.get('email', None)
            assert email
        except AssertionError:
            logger.debug('Email Field is required for ValidateTrialUser endpoint')
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'status': 'Error', 'message': 'email required.'})

        try:
            email_domain = email.split('@')[1]
        except (IndexError, AttributeError):
            logger.debug("Can't find an email address: {}".format(email))
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={
                    'status': 'Error',
                    'message': 'Can\'t find an email address. Please try again.'
                })
        resume_count = ResumeModel.objects.filter(
            trial_user__email_address=email
        ).count()

        if resume_count >= RESUME_THRESHOLD_COUNT_FOR_TRIAL_VERSION:
            logger.debug('{} already used for trial version'.format(email))
            return Response({
                    'status': 'failure',
                    'message': 'This email has already been used for the trial version.'
                }, status=status.HTTP_403_FORBIDDEN)

        # validating email address, as well as DNS, MX existence, and ESP
        # grammar checks.
        if address.validate_address(email) is None:
            logger.debug('{} is not a valid email address'.format(email))
            return Response({
                    'status': 'failure',
                    'message': 'Please enter a valid email address.'
                }, status=status.HTTP_403_FORBIDDEN)

        if email_domain in DESPOSABLE_EMAIL_DOMAINS:
            logger.debug('{} is present in DESPOSABLE_EMAIL_DOMAINS'.format(email_domain))
            return Response({
                    'status': 'failure',
                    'message': 'Please use a valid email address.'
                }, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'status': 'success',
            'message': email + ' is valid.'
        }, status=status.HTTP_200_OK)


class ResumeFilterDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        resume_id = kwargs.get('id')
        try:
            UUID(resume_id)
        except ValueError:
            logger.debug('Resume ID: {} is not a valid uuid'.format(resume_id))
            return Response({'message': 'uuid not valid'}, status=400)

        try:
            instance = ResumeModel.objects.get(id=resume_id)
        except ResumeModel.DoesNotExist:
            logger.debug('Resume for resume_id: {} does not exist'.format(resume_id))
            raise Http404

        ## dynamic skills details calculation
        skills = request.query_params.get('skills', '')
        if skills:
            skills = skills.lower()
            skills = skills.split(',')
        else:
            skills = []

        ser = ResumeSerializer(
            instance=instance, context = {'skills': skills}
        )
        return Response(ser.data)


class ResumePersonalView(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        form = UploadResumeForm(request.POST, request.FILES)
        if form.is_valid():
            get_file = request.FILES['file']
            file_name = get_file.name.lower()
            name, ext = os.path.splitext(file_name)
            uploaded_file_name = default_storage.save(
                "%s" % uuid4() + ext, ContentFile(get_file.read()))
            path = default_storage.open(uploaded_file_name).name
            first_name, last_name, phone_number, email = get_basics(path)
            return Response({'status': 'Successfully Parsed',
                             'first_name': first_name,
                             'last_name': last_name,
                             'phone_number': phone_number,
                             'email': email}, status=status.HTTP_200_OK)
        return JsonResponse(form.errors)


class Resume(generics.GenericAPIView):
    """
    Resume View for get and post request.
    """
    serializer_class = ResumeSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = ResumeModel.objects.filter()

    def post(self, request, *args, **kwargs):
        # TODO(kaviraj): Need serious cleanup

        """

        Upload a Resume File and skills.
        ---
        parameters:
            - name: file
              type: file
            - name: skills
              type: string

        """
        if request.user.resumes.count() >= UserProfile.objects.get(user=request.user).limit:
            logger.debug('Resume upload limit exceeded for user: {}'.format(request.user))
            return Response({
                'status': 'Failed',
                'message': 'Resume upload limit exceeded.'
            }, status=status.HTTP_403_FORBIDDEN)

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            get_file = request.FILES['file']
            file_name = get_file.name.lower()
            name, ext = os.path.splitext(file_name)
            if settings.UPLOAD_TO_S3:
                path = upload_to_s3(get_file, name, ext)
            else:
                uploaded_file_name = default_storage.save(
                    "%s" % uuid4() + ext, ContentFile(get_file.read()))
                path = default_storage.open(uploaded_file_name).name

            cd = form.cleaned_data
            skills = ''
            text = get_text(path)
            if not text or len(text) < 200:
                text = get_text_via_ocr(path)
            # celery task
            content_hash = get_sim_hash_for_resume_content(text)
            hash_value = content_hash.value

            # TODO(kaviraj): Need to rethink about hashing. Seems like not scalable
            list_hash_values = filter(
                None,
                ResumeModel.objects.values().values_list(
                    'content_hash', flat=True).filter(trial_user__isnull=True)
            )

            if not list_hash_values:
                resume_instance = ResumeModel.objects.create(
                    user=request.user,
                    parse_status=ResumeModel.STATUS.processing
                )
                resume_id = resume_instance.id
                parse_resume.delay(path, text, resume_id,
                                   skills, file_name, hash_value)
                resume_status = resume_instance.get_parse_status_display()
                new_response = {'status': resume_status,
                                'resume_id': resume_id}
                return JsonResponse(new_response)

            check_present_values = check_hamming_distance(
                list_hash_values, hash_value)
            value = check_present_values[1]
            if check_present_values[0]:
                # TODO(kaviraj): Need to handle filter[0] index error?
                resume_instance = ResumeModel.objects.filter(
                    content_hash=str(value))[0]
                resume_id = resume_instance.id

                resume_skills = [skill.name for skill in list(
                    resume_instance.skills.all())]
                new_skills = skills.lower().split(',')
                new_skills = [skill.strip() for skill in new_skills if skill.strip()]
                if set(resume_skills) == set(new_skills):
                    resume_status = resume_instance.get_parse_status_display()
                    new_response = {'status': resume_status,
                                    'resume_id': resume_id}
                    return JsonResponse(new_response)

            resume_instance = ResumeModel.objects.create(
                user=request.user,
                parse_status=ResumeModel.STATUS.processing
            )
            resume_id = resume_instance.id
            parse_resume.delay(path, text, resume_id,
                               skills, file_name, hash_value)
            resume_status = resume_instance.get_parse_status_display()
            new_response = {'status': resume_status,
                            'resume_id': resume_id}
            # default_storage.headers.clear()
            return JsonResponse(new_response)

        logger.debug(form.errors)
        return JsonResponse(form.errors)


class ResumeBasicDetailsView(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        form = UploadResumeForm(request.POST, request.FILES)
        if not form.is_valid():
            return Response(form.errors)

        f = request.FILES.get('file', None)
        if not f:
            return Response({
                'message': 'Cannot proceed further. File is missing.'
            }, status = status.HTTP_400_BAD_REQUEST)

        # Basic file storage on a local filesystem.
        fs = FileSystemStorage()
        # Save file.
        filename = fs.save("temp+" + f.name.lower(), f)
        # Absolute path to the directory that will hold the files.
        path = fs.location + '/' + filename

        # Get basic resume details.
        first_name, last_name, phone_number, email = get_basics(path)
        # Delete file as it was temporary.
        fs.delete(filename)

        return Response({
            'email': email,
            'last_name': last_name,
            'first_name': first_name,
            'phone_number': phone_number,
            'status': 'Successfully parsed.'
        }, status=status.HTTP_200_OK)


class ResumeParseInternal(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = [AllowInternalServiceOnly]
    serializer_class = ResumeParseInternalSerializer

    def post(self, request, *args, **kwargs):
        f = request.FILES.get('file', None)
        if not f:
            logger.debug('Resume file not provided. Used against ResumeParseInternal endpoint')
            return Response({
                'status': 'failure',
                'message': 'Cannot proceed further. File is missing.'
            }, status = status.HTTP_400_BAD_REQUEST)

        # Get resume_id or create on our own.
        resume_id = request.data.get('resume_id', None)
        if not resume_id:
            resume_id = str(uuid4())

        # Get file name and extension from provided file.
        f_name, f_ext = os.path.splitext(f.name.lower())
        # If file name is large; truncate.
        f_name[:40] if len(f_name) > 40 else f_name

        # Save resume to default storage.
        uploaded_fname = default_storage.save(
            resume_id + f_ext, ContentFile(f.read())
        )
        # Get path of stored resume.
        path = default_storage.url(
            default_storage.open(uploaded_fname).name
        )

        text = get_text(path)
        if not text or len(text) < 200:
            # Guess is that; it might be an image (in PDF).
            text = get_text_via_ocr(path)

        hash_value = get_sim_hash_for_resume_content(text)
        if hash_value:
            hash_value = hash_value.value

        serializer_data = create_resume_instance(
            path, text, f_name, hash_value, request.user, request.data
        )

        return Response(serializer_data)


class SampleResumeView(generics.GenericAPIView):

    def get_serializer_class(self, *args, **kwargs):
        # return different serializer depending on method
        return ResumeSerializer

    def post(self, request, *args, **kwargs):
        form = SampleResumeForm(request.POST)
        if form.is_valid():
            clean_data = form.cleaned_data
            file_name = clean_data.get('file', None)
            skills = clean_data.get('skills', None)
            email = clean_data.get('email', None)

            if not resume.models.TrialUser.objects.filter(email_address=email):
                # TODO(kaviraj):
                # Need to refactor(no email hardcoding, elegant deep copy)

                try:
                    resume_data = ResumeModel.objects.get(
                        file_name=file_name, trial_user__email_address='sample@aircto.com')
                except ResumeModel.DoesNotExist:
                    logger.debug('Sample Resume could not be found for file_name: {}.'.format(file_name))
                    return Response(
                        status=status.HTTP_404_NOT_FOUND,
                        data = {'status': '404', 'message': 'Sample data not found.'},
                    )
                trial_user_instance = resume.models.TrialUser.objects.create(
                    email_address=email,
                )
                resume_instance = deepcopy(resume_data)
                resume_instance.pk = None
                resume_instance.id = None
                resume_instance.save()
                copy_reverse_relations(
                    resume_instance, resume_data.stackoverflow_set.all())
                copy_reverse_relations(
                    resume_instance, resume_data.resumeskills_set.all())
                copy_reverse_relations(
                    resume_instance, resume_data.github_set.all())
                copy_reverse_relations(
                    resume_instance, resume_data.bitbucket_set.all())
                copy_reverse_relations(
                    resume_instance, resume_data.blog_set.all())
                copy_reverse_relations(
                    resume_instance, resume_data.mobileapp_set.all())
                copy_reverse_relations(
                    resume_instance, resume_data.website_set.all())
                resume_instance.scores = resume_data.scores.all()
                resume_instance.urls = resume_data.urls.all()
                resume_instance.trial_user = trial_user_instance
                resume_instance.save()
                new_response = {'status': resume_instance.get_parse_status_display(),
                                'resume_id': resume_instance.id}
            else:
                new_response = {'message': 'Email Address already used. Try with another one.'
                                }

            return Response(new_response)

        logger.debug(form.errors)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class TrialUserView(generics.GenericAPIView, RatelimitMixin):
    ratelimit_key = "ip"
    ratelimit_rate = "50/h"
    ratelimit_method = UNSAFE
    # Add more here as you wish
    throttle_classes = (throttling.UserRateThrottle,)
    # This is the default already, but let's be specific anyway
    throttled_exception_class = rest_exceptions.CustomThrottled

    def get_throttled_message(self):
        """Add a custom message to the throttled error."""
        return "request limit exceeded"

    def get_serializer_class(self, *args, **kwargs):
        # return different serializer depending on method
        return ResumeSerializer

    def post(self, request):
        form = TrialUseCaseForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            user_email = cleaned_data.get('email_address', None)
            resume_file = request.FILES.get('file', None)
            file_name = resume_file.name.lower()
            name, ext = os.path.splitext(file_name)
            if settings.UPLOAD_TO_S3:
                path = upload_to_s3(resume_file, name, ext)
                print(("uploaded path", path))
            else:
                uploaded_file_name = default_storage.save(
                    "%s" % uuid4() + ext, ContentFile(resume_file.read()))
                path = default_storage.open(uploaded_file_name).name
            # path = upload_to_s3(resume_file, name, ext)
            cd = form.cleaned_data
            skills = cd['skills']
            text = get_text(path)

            # celery task
            content_hash = get_sim_hash_for_resume_content(text)
            hash_value = content_hash.value
            trial_user_instance = resume.models.TrialUser.objects.create(
                email_address=user_email,
            )
            resume_instance = ResumeModel.objects.create(
                trial_user=trial_user_instance,
                parse_status=ResumeModel.STATUS.processing
            )
            parse_resume.delay(
                path, text, resume_instance.id, skills, file_name, hash_value
            )
            response = {
                'status': resume_instance.get_parse_status_display(),
                'resume_id': resume_instance.id
            }
            return Response(response)
        logger.debug(form.errors)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class SampleResumeDetailView(generics.RetrieveAPIView):
    """View for Sample Resume"""
    queryset = ResumeModel.objects.filter(trial_user__isnull=False)
    serializer_class = ResumeSerializer
    lookup_field = 'id'


class ResumeDetailView(generics.RetrieveAPIView):
    queryset = ResumeModel.objects.filter(trial_user__isnull=True)
    serializer_class = ResumeSerializer
    lookup_field = 'id'


class TrialResumeDetailView(generics.RetrieveAPIView):
    queryset = ResumeModel.objects.filter(trial_user__isnull=False)
    serializer_class = ResumeSerializer
    lookup_field = 'id'


class ResumeSyncView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        resume_id = request.data.get("resume_id", None)
        try:
            UUID(resume_id)
        except ValueError:
            logger.debug('Resume id: {} is not a valid uuid'.format(resume_id))
            return Response({"message": "not a valid uuid"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = ResumeModel.objects.get(id=resume_id)
        except ResumeModel.DoesNotExist:
            logger.debug('Resume id {} not found'.format(resume_id))
            raise Http404("resume_id not found")

        instance.first_name = request.data.get("first_name", instance.first_name)[:50]
        instance.last_name = request.data.get("last_name", instance.last_name)[:50]
        instance.email = request.data.get("email", instance.email)[:50]
        instance.save()

        return Response({"message": "success"}, status=status.HTTP_200_OK)


class GetUploadLimitView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        latest_skills_used = []
        user_profile = request.user.profile
        resume_upload_limit = user_profile.limit

        uploaded = ResumeModel.objects.filter(
            user__profile=user_profile
        ).count()

        try:
            latest_skills_used = list(
                request.user.resumes.order_by('-created_date')[0].skills.all()
            )
        except IndexError:
            logger.debug('Not enough Resume for user: {}'.format(request.user))
            print("Not enough Resume")

        skills_asked = [item.name for item in latest_skills_used if item.name.strip()]
        response = {
            'upload_limit': resume_upload_limit,
            'latest_skills_used': skills_asked,
            'upload_remaining': resume_upload_limit - uploaded
        }
        return Response(response)


@method_decorator(store_visitor_activity, name='dispatch')
class ResumeFilter(APIView):
    permission_classes = (IsAuthenticated,)

    # TODO (Mohsin):
    #   - Handle exception while accessing 'fetchall' func.
    def __init__(self, *args):
        self.FUZZ_RATIO = 95
        self.exp_matched, self.exp_unmatched = 0.0, 0.0
        self.skills_matched, self.skills_unmatched = list(), list()
        self.degrees_matched, self.degrees_unmatched = list(), list()
        self.top_coll_matched, self.top_coll_unmatched = list(), list()
        self.companies_matched, self.companies_unmatched = list(), list()
        self.locations_matched, self.locations_unmatched = list(), list()

    def post(self, request, *args, **kwargs):
        response_list = list()
        resume_ids = clean_list_items(request.data.get('resume_ids', None))
        if not resume_ids:
            return Response(
                data={"error": "No resume id(s) provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        for resume_id in resume_ids:
            # Get resume instance.
            try:
                resume = ResumeModel.objects.get(id=resume_id)
            except ResumeModel.DoesNotExist:
                continue

            # Resume details.
            self.resume_id = resume_id
            self.resume_content = resume.content

            self._scan_skills(request)
            self._scan_degrees(request)
            self._scan_companies(request)
            self._scan_locations(request)
            self._scan_experience(request)
            self._scan_top_colleges(request)
            response_list.append(self.get_resume_criteria())

        return Response({"data": response_list}, status=status.HTTP_200_OK)

    def get_resume_criteria(self):
        get_mu = get_matched_unmatched
        return {
            "resume_id": self.resume_id,
            "experience": get_mu(self.exp_matched, self.exp_unmatched),
            "skills": get_mu(self.skills_matched, self.skills_unmatched),
            "degrees" : get_mu(self.degrees_matched, self.degrees_unmatched),
            "companies": get_mu(self.companies_matched, self.companies_unmatched),
            "locations": get_mu(self.locations_matched, self.locations_unmatched),
            "top_colleges": get_mu(self.top_coll_matched, self.top_coll_unmatched)
        }

    def _scan_degrees(self, request):
        degrees = clean_list_items(request.data.get('degrees', None))
        if not degrees:
            return

        content_set = set(self.resume_content.lower().split())
        for degree in degrees:
            if content_set != set():
                # Find the closest match(es) from list.
                scanned_degree, ratio = process.extractOne(degree, content_set)
                if ratio >= self.FUZZ_RATIO:
                    self.degrees_matched.append(degree)
                    print("INFO: _scan_degrees: ", scanned_degree, degree, ratio)

        self.degrees_unmatched = list_sym_difference(degrees, self.degrees_matched)
        return

    def _scan_skills(self, request):
        q = (
        """
            SELECT rs.name FROM resume_resumeskills AS rrs
            JOIN resume_skill AS rs ON rs.id = rrs.skill_id
            WHERE rrs.resume_id = '{}'
        """
        )

        given_skills = map_to_lower(
            clean_list_items(request.data.get('skills', None))
        )
        if not given_skills:
            return

        resume_skills = chain_iters(exec_fetch_all(q.format(self.resume_id)))
        self.skills_matched, self.skills_unmatched = get_matched_unmatched_skills(
            given_skills, resume_skills
        )
        return

    def _scan_top_colleges(self, request):
        q = (
        """
            SELECT ri.name, ri.score FROM resume_institution AS ri
            JOIN resume_resume_institutions AS rri ON ri.id=rri.institution_id
            WHERE rri.resume_id = '{}'
        """
        )

        should_be_top_colleges = request.data.get('top_colleges')
        if not should_be_top_colleges:
            return

        resume_coll = exec_fetch_all(q.format(self.resume_id))
        for name, score in resume_coll:
            (
                self.top_coll_matched.append(name)
                if 1 <= score <= 100
                else self.top_coll_unmatched.append(name)
            )
        return

    def _scan_experience(self, request):
        q = ("SELECT experience FROM resume_resume WHERE id = '{}'")

        exp_min = request.data.get('exp_min', None)
        exp_max = request.data.get('exp_max', None)

        try:
            if exp_min:
                exp_min = float(exp_min)
            if exp_max:
                exp_max = float(exp_max)
        except ValueError:
            return

        # DB query.
        exp = exec_fetch_one(q.format(self.resume_id))
        if not exp:
            return
        exp = exp[0]

        # For both exp_min and exp_max.
        if (exp_min and exp_max) and (exp_min <= exp <= exp_max):
            self.exp_matched = exp
            return

        # For exp_min.
        if exp_min and (exp >= exp_min):
            self.exp_matched = exp
            return

        # For exp_max.
        if exp_max and (exp <= exp_max):
            self.exp_matched = exp
            return

    def _scan_companies(self, request):
        q = (
        """
            SELECT rc.name FROM resume_resume_companies AS rrc
            JOIN resume_company AS rc ON rc.id=rrc.company_id
            WHERE rrc.resume_id = '{0}' AND rc.name ~* '{1}'
        """
        )

        companies = clean_list_items(request.data.get('companies', None))
        if not companies:
            return

        self.companies_matched = chain_iters(
            exec_fetch_all(q.format(self.resume_id, pipe_sep.join(companies)))
        )
        self.companies_unmatched = list_sym_difference(companies, self.companies_matched)
        return

    def _scan_locations(self, request):
        q = (
        """
            SELECT rl.name FROM resume_resume_locations AS rrl
            JOIN resume_location AS rl ON rl.id=rrl.location_id
            WHERE rrl.resume_id = '{0}' AND rl.name ~* '{1}'
        """
        )

        locations = clean_list_items(request.data.get('locations', None))
        if not locations:
            return

        self.locations_matched = chain_iters(
            exec_fetch_all(q.format(self.resume_id, pipe_sep.join(locations)))
        )
        self.locations_unmatched = list_sym_difference(locations, self.locations_matched)
        return

# Helpers ----------------------------------------------------------------------

# TODO (Mohsin): Refactor/Optimize.
def get_matched_unmatched_skills(given_skills, resume_skills):
    FUZZ_RATIO = 90
    js_skills = ('js', '.js', 'javascript')
    matched_skills, unmatched_skills = list(), list()
    given_js_skills, given_other_skills = list(), list()
    resume_js_skills, resume_other_skills = list(), list()
    matched_js_skills, unmatched_js_skills = list(), list()
    matched_other_skills, unmatched_other_skills = list(), list()

    for skill in resume_skills:
        target = resume_js_skills if skill.endswith(js_skills) else resume_other_skills
        target.append(skill)

    for skill in given_skills:
        target = given_js_skills if skill.endswith(js_skills) else given_other_skills
        target.append(skill)

    for skill in given_js_skills:
        if resume_js_skills != list():
            # Find the closest match(es) from list.
            _, ratio = process.extractOne(skill, resume_js_skills)
            target = matched_js_skills if ratio >= FUZZ_RATIO else unmatched_js_skills
            target.append(skill)

    for skill in given_other_skills:
        if resume_other_skills != list():
            # Find the closest match(es) from list.
            _, ratio = process.extractOne(skill, resume_other_skills)
            target = matched_other_skills if ratio >= FUZZ_RATIO else unmatched_other_skills
            target.append(skill)

    matched_skills = matched_js_skills + matched_other_skills
    unmatched_skills = unmatched_js_skills + unmatched_other_skills

    return matched_skills, unmatched_skills

# get_matched_unmatched should return dict with matched and unmatched keys by
# considering provided lists through function params, for the same.
def get_matched_unmatched(matched, unmatched):
    return {
        "matched": matched,
        "unmatched": unmatched
    }

# chain_iters should create a single list of iterables by chaining 'em.
def chain_iters(iterables):
    return list(itertools.chain(*iterables))

# list_sym_difference should return list which contains unique values from
# provided two lists.
def list_sym_difference(whole, part):
    return list(set(whole).symmetric_difference(part))

# map_to_lower should return container values by converting it to lowercase.
def map_to_lower(container):
    return map(lambda x:x.lower(), container)

# clean_list_items should return list by converting unicode to string and by
# not considering empty/nil values.
def clean_list_items(container):
    if container:
        return [str(item).lower() for item in container if item]
    return list()

# exec_fetch_one should fetch one field value for provided query and return it.
def exec_fetch_one(query):
    cursor = connection.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    return row

# exec_fetch_all should fetch all field values for provided query and return it.
def exec_fetch_all(query):
    cursor = connection.cursor()
    cursor.execute(query)
    row = cursor.fetchall()
    return row

def copy_reverse_relations(new_resume, queryset):
    for instance in queryset:
        instance.id = None
        instance.resume = new_resume
        instance.save()

# ------------------------------------------------------------------------------
