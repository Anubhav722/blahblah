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
    help = "Management command to alter resumes information."
    option_list = BaseCommand.option_list + (
            make_option('--update-rankings',
                action='store_true',
                dest='update_rankings',
                help='Update the rankings of resume objects.'
            ),
    )

    def update_rankings(self, ids=[]):
        resumes = Resume.objects.all()
        if ids:
            resumes = Resume.objects.filter(id__in=ids)

        for resume in resumes:
            serializer = ResumeSerializer(resume)
            data = serializer.data
            ranking_score = (
                item for item in data['score'] if item["name"] == "Ranking"
            ).next()['data']
            obtained_score = ranking_score[0]['obtained']
            self.stdout.write("Updating... {}".format(resume.file_name))
            Resume.objects.filter(id=resume.id).update(
                total_score=obtained_score, hireable=hireable(obtained_score)
            )

    def handle(self, *args, **options):
        try:
            if options['update_rankings']:
                assert args
                self.update_rankings(ids=list(args))
            else:
                self.update_rankings()
        except AssertionError:
            print ("Please provide resume IDs.")
        except Exception:
            raise CommandError("An error has occurred.")
