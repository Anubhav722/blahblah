from django.core.management.base import BaseCommand, CommandError
from jarvis.resume.utils import benchmarker


class Command(BaseCommand):

    def handle(self, *args, **options):
        # benchmarker.run_benchmarker()
        pass
