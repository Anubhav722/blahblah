from django.core.management.base import BaseCommand, CommandError
import csv, gensim, os

from django.conf import settings

class Command(BaseCommand):
    help = "Create skill index for all the extracted skills"

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str)
        parser.add_argument('--output', type=str)

    def handle(self, *args, **options):
        if not options['csv']:
            raise Exception("Please provide skills' .csv filename")

        file = options['csv']
        csv_file_path = os.path.dirname(settings.BASE_DIR) + '/{}'.format(file)
        with open(csv_file_path, 'rb') as f:
            reader = csv.reader(f)
            skills_list = list(reader)

        if options['output']:
            path = options['output']
            model = gensim.models.Word2Vec(skills_list, min_count=1)
            model.save(path)

        else:
            model.save('aircto.index')