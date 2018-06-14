import requests

# Miscellaneous
from optparse import make_option

# Django Imports
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

# App Imports
from jarvis.resume.models import Resume
from jarvis.resume.helpers import hireable
from jarvis.resume.api.serializers import ResumeSerializer


class Command(BaseCommand):
    help = "Management command to sync resumes information from aircto-backend."
    option_list = BaseCommand.option_list + (
            make_option('--token',
                action='store',
                dest='token',
                help='update resume objects with aircto-backend.'
            ),
        make_option('--endpoint',
                action='store',
                dest='endpoint',
                help='sync-endpoint.'
            ),

    )

    def sync(self, endpoint, token, ids=[]):
        for id in ids:
            url = endpoint + "/" + id
            resp = requests.get(url, headers={'Authorization': 'Token '+token})
            if resp.status_code != 200:
                print((resp.json()))
                continue;
            d = resp.json()
            try:
                resume = Resume.objects.get(id=id)
            except:
                print(("object not found ", id))
                continue

            # import ipdb; ipdb.set_trace()
            results = d.get('data')
            if not results:
                print(("invalid response", d))
                continue
            resume.phone_number = results.get('primary_contact', resume.phone_number)

            candidate = results.get('candidate')

            if candidate:
                resume.first_name = candidate.get('first_name', resume.first_name)
                resume.last_name = candidate.get('last_name', resume.last_name)
                resume.email = candidate.get('email', resume.email)
            resume.save()
            print(("processed success: ", resume.id))

    def handle(self, *args, **options):
        endpoint = options.get('endpoint', None)
        token = options.get('token',None)

        if not (endpoint and token):
            raise "need endpoint and token"

        ids = Resume.objects.all().values_list('id', flat=True)
        ids = [str(x) for x in ids]
        self.sync(endpoint, token, ids)
