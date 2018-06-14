
import requests
import urllib2
from bs4 import BeautifulSoup
from unidecode import unidecode
import string
from nltk.corpus import stopwords
import csv
import pandas as pd
from jarvis.resume.models import Company, Institution, Location
import math


class Skills:

    def text_process(self, text):
        """
        Takes in a string of text, then performs the following:
        1. Remove all punctuation
        2. Remove all stopwords
        3. Returns a list of the cleaned text
        """
        # Check characters to see if they are in punctuation
        nopunc = [char for char in text if char not in string.punctuation]

        # Join the characters again to form the string.
        nopunc = ''.join(nopunc)

        # Now just remove any stopwords
        return [word for word in nopunc.split() if word.lower() not in stopwords.words('english')]

    def search_skill(self, skill):
        """
        This method uses Dice API to search for Jobs based on skill provided
        :param skill: string
        :return: list of details - job title and url of the job.
        """
        try:
            details = []
            for page_no in range(1, 50):
                print("page no. : {}".format(page_no))
                url = 'http://service.dice.com/api/rest/jobsearch/v1/simple.json?text=%s&page=%s' % (skill, page_no)
                request = requests.get(url).json()
                if 'resultItemList' in list(request.keys()):
                    url_list = request['resultItemList']
                    if url_list:
                        for detail in url_list:
                            detail_url = detail['detailUrl']
                            details.append({'detail_url': detail_url})
            return details
        except Exception as error:
            print("search_skill, %s " % error)


    def scrape_url(self, url):
        """
        This method scrape the job url and extract job description.
        :param url: string: url
        :return: string
        """
        print("scrape_url, %s " % url)
        try:
            page = urllib.urlopen(url)
            soup = BeautifulSoup(page, 'lxml')
            job_desc = soup.find('div', {'id': 'jobdescSec'}).text
            job_desc = unidecode(job_desc)
            job_desc = job_desc.replace('\n', '')
            job_desc = job_desc.replace('\t', '')
            job_desc = job_desc.replace('\r', '')
            return job_desc
        except Exception as error:
            print("scrape_url, %s " % error)


    def get_details(self, skill):
        """
        This method extracts title and job description.
        :param skill: string
        :return: dictionary
        """
        try:
            print("get_details , %s " % skill)
            search = self.search_skill(skill)
            search = search[:50]
            details = []
            if search:
                search = [_f for _f in search if _f]
                search_skill = search[:50]
                for item in search_skill:
                    if item:
                        url = item['detail_url']
                        text = self.scrape_url(url)
                        text = self.text_process(text)
                        details.append(text)
            return details
        except Exception as error:
            print("get_details, %s " % error)

    def get_all_tags(self):
        """
        This method extracts all the skills from StackOverflow website.
        :return: creates a csv file with all the tags found.
        """
        try:
            all_skills = ['Skills']
            for page in range(1, 20):
                url = 'https://api.stackexchange.com/2.2/tags?page=%s&pagesize=100&order=desc&sort=popular&site=stackoverflow' % page
                tag_request = requests.get(url).json()
                if tag_request['items']:
                    for skill in tag_request['items']:
                        skill_name = skill['name']
                        all_skills.append(skill_name)
            with open("all_skills.csv", 'wb') as my_file:
                wr = csv.writer(my_file)
                for skill in all_skills:
                    wr.writerow([skill])
                my_file.close()
        except Exception as error:
            print(error)

    def extract_skills_job_description(self):
        """
        This method extract all matched skills between job descriptions and skills from StackOverflow
        :return: creates a csv file
        """
        # list_of_jobs = ['reactjs', 'django', 'ios developer']
        jobs = ['iOs Developer', 'PHP developer', 'Frontend engineer', 'Reactjs', 'Ruby On Rails', 'Devops',
                'SAP', 'Javascript', 'Python', 'Quality Assurance (QA)', 'Nodejs', 'Java', 'Django', 'Android',
                'UI engineer', 'UX engineer', 'MEAN stack', 'Machine Learning', 'backend', 'data analysis'
                ]
        list_of_jobs = [skill.lower() for skill in jobs]
        # uncomment the below line to create a csv file for all the skills from StackOverflow in the current directory.
        # self.get_all_tags()
        df_skills = pd.read_csv('all_skills.csv')
        all_skills = list(df_skills['Skills'])
        all_skills = [_f for _f in all_skills if _f]
        descriptions = []
        skills_found = []
        try:
            for skill in list_of_jobs:
                descriptions.append(self.get_details(skill))
            print("descriptions done")
            descriptions = [_f for _f in descriptions if _f]
            for items in descriptions:
                items = [_f for _f in items if _f]
                for skill in items:
                    skill = [_f for _f in skill if _f]
                    skill_new = [s for s in skill if s is not None]
                    skill_new = [s for s in skill_new if s is not ""]
                    skill_new = [s.lower() for s in skill_new]
                    skills_found.append(list(set(skill_new) & set(all_skills)))
            with open('all_details.csv', 'wb') as my_file:
                wr = csv.writer(my_file)
                for skill_list in skills_found:
                    wr.writerow([skill_list])
                    print("row written %s " % skill_list)
                my_file.close()
        except Exception as error:
            print(error)

    def extract_skills(self, url, file_name, pages):
        """
        This method extract key skills of the job.
        :param url: Naurki's url of the job -- 'https://www.naukri.com/php-developer-jobs'
        :param file_name: string: file name of output csv file.
        :param pages: int: number of pages to extract from naukri.com
        :return:
        """
        try:
            job_urls = []
            all_key_skills = []
            for page_no in range(1, pages):
                url = '%s-%s' % (url, page_no)
                request = requests.get(url).text
                soup = BeautifulSoup(request, 'lxml')
                for url in soup.find_all('a', href=True):
                    if 'job-listings' in url['href']:
                        job_urls.append(url['href'])
                job_urls = [_f for _f in job_urls if _f]
                print('-----------------------------')
                print('all job urls extracted from page %s' % page_no)
                print('-----------------------------')
                print('extracting key skills from each url.........')
                print('-----------------------------')
                for url in job_urls:
                    print('-----------------------------')
                    print('key skills: %s' % url)
                    print('-----------------------------')
                    job_request = requests.get(url)
                    if job_request.text:
                        job_soup = BeautifulSoup(job_request.text, 'lxml')
                        find_tags = job_soup.find("div", {'class': 'ksTags'})
                        if find_tags:
                            find_key_skills = ', '.join([item.text.strip() for item in find_tags.find_all('a')])
                            key_skills = find_key_skills.strip()
                            key_skills = unidecode(key_skills)
                            key_skills = key_skills.replace('\n', '')
                            key_skills = key_skills.replace('\r', '')
                            key_skills = key_skills.replace('\t', '')
                            all_key_skills.append(key_skills)
                print("length of all_key_skills: ", len(all_key_skills))
                print('-----------------------------')
                print('writing to csv file....')
                print('-----------------------------')
                with open(file_name, 'wb') as my_file:
                    wr = csv.writer(my_file)
                    for skill_list in all_key_skills:
                        wr.writerow([skill_list])
                    my_file.close()
            print('file written - %s' % file_name)
        except Exception as error:
            return error


def fill_company_model():
    file_path = '/home/launchyard/Work/parser/filter-api/jarvis/resume/utils/machine_learning/data/all_companies.xlsx'
    df = pd.read_excel(file_path)
    for item in df.iterrows():
        if (math.isnan(item[1]['Location'])) and (math.isnan(item[1]['Brand Rank'])):
            Company.objects.create(location=None, company=item[1]['Company Names'], rank=None)
        elif (math.isnan(item[1]['Location'])) and (not math.isnan(item[1]['Brand Rank'])):
            Company.objects.create(location=None, company=item[1]['Company Names'], rank=item[1]['Brand Rank'])
        elif (not math.isnan(item[1]['Location'])) and (math.isnan(item[1]['Brand Rank'])):
            Company.objects.create(location=item[1]['Location'], company=item[1]['Company Names'], rank=None)


def fill_institution_model():
    file_path = '/home/launchyard/Work/parser/filter-api/jarvis/resume/utils/machine_learning/data/all_colleges.csv'
    df = pd.read_csv(file_path)
    try:
        for item in df.iterrows():
            if (type(item[1]['City']) == str) and (type(item[1]['Score']) == float):
                if math.isnan(item[1]['Score']):
                    location_name = item[1]['City'].lower()
                    location_instance, check = Location.objects.get_or_create(location=location_name)
                    Institution.objects.create(location=location_instance, institution=item[1]['Institution Names'], score=None)
                else:
                    location_name = item[1]['City'].lower()
                    location_instance, check = Location.objects.get_or_create(location=location_name)
                    Institution.objects.create(location=location_instance, institution=item[1]['Institution Names'],
                                               score=item[1]['Score'])
            elif (type(item[1]['City']) == float) and (type(item[1]['Score']) == float):
                if (math.isnan(item[1]['Score'])) and (math.isnan(item[1]['City'])):
                    Institution.objects.create(location=None, institution=item[1]['Institution Names'], score=None)
        return 'details imported.'
    except Exception as error:
        print(error)


def fill_location_model():
    return NotImplementedError

