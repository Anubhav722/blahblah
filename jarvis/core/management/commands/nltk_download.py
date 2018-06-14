import nltk

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Download NLTK corpus"

    def add_arguments(self, parser):
        parser.add_argument('corpus_name')

    def handle(self, *args, **options):
        corpus_name = options['corpus_name']
        nltk.download(corpus_name)
