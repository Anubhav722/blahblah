from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
import requests

from optparse import make_option
import csv
import argparse
import gensim, logging

JOB_PAGINATION = 50



def fetch_skills(soup, limit, count):
    all_skills = []
    for link in soup.findAll(attrs={'class':'content'}):
        if count > limit:
            break

        detail_url = link.get('href')
        r = requests.get(detail_url)
        data = r.text
        detail_soup = BeautifulSoup(data, 'html5lib')

        skills = [skill.text for skill in detail_soup.findAll(attrs={'class':'hlite'})]
        all_skills.append(skills)
        count += 1

    return (all_skills, count)


class Command(BaseCommand):
    help = "Management command to extract skills from naukri.com"

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int)
        parser.add_argument('--job', help='Search for skills for that job profile', nargs='+')
    

    def handle(self, *args, **options):

        if not options['job'] or options['limit']:
            raise Exception('Please provide job profile or limit')


        job_profile = options['job']
        job_profile = "-".join(job_profile) + '-jobs'

        main_url = 'https://www.naukri.com/{}'.format(job_profile)

        all_skills = []
        skills = []
        limit = options['limit']
        count = 0

        for page in range(limit/JOB_PAGINATION+1):
            if page != 1:
                url = main_url + '-{}'.format(page)

            r = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data, 'html5lib')

            skills, count = fetch_skills(soup, limit, count)
            all_skills = all_skills + skills

            url = main_url

        if limit < JOB_PAGINATION and len(all_skills) == 0:
            r = requests.get(main_url)
            data = r.text
            soup = BeautifulSoup(data, 'html5lib')

            all_skills = fetch_skills(soup)


        with open('skills.csv', 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(all_skills)
            print ('Skills successfully extracted.')
