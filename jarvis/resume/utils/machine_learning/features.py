from unidecode import unidecode
from unicodedata import normalize as _uni_normalize
import string
from nltk.corpus import stopwords
import pandas as pd
import spacy
from django.conf import settings
import re

from django.db.models.functions import Lower

from jarvis.resume.models import Location, Company, Institution
from .constants import (
    SUMMARY_OBJECTIVE_HEADINGS, EXPERIENCE_HEADINGS, EDUCATION_HEADINGS,
    SKILLS_HEADINGS, CONTACT_HEADINGS, RECHECK_THRESHOLD
)
from functools import reduce


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class IndexHeadings:
    """
    Index headings of given resume text.
    """

    def __init__(self):
        pass

    def create_paragraphs(self, text):
        summary_index = -1
        experience_index = -1
        education_index = -1
        skills_index = -1
        contact_index = -1

        summary_and_contact_headings = reduce(
            tuple.__add__, [
                SUMMARY_OBJECTIVE_HEADINGS,
                CONTACT_HEADINGS
            ]
        )

        custom_headings = reduce(
            tuple.__add__, [
                EXPERIENCE_HEADINGS, EDUCATION_HEADINGS, SKILLS_HEADINGS,
                CONTACT_HEADINGS
            ]
        )

        cleaned_paragraphs = list()
        text = text.lower().strip()
        try:
            text = _uni_normalize('NFKD', text)
        except TypeError:
            pass
        text = re.sub(' +', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub("[ \t\r\f\v]+", " ", text)

        end_marker = 0
        reference_marker = 0
        summary_index_marked = 0
        contact_index_marked = 0
        found_reference_marker = 0

        lines = re.split('\n', text)

        # Create starting index
        for substring in summary_and_contact_headings:
            for index, line in enumerate(lines):
                line = line.strip()
                line = line.replace(":-", "").replace(":", "").replace("-", "").replace(".", "")

                if not found_reference_marker:
                    # if substring == line:
                    if line.startswith(substring):
                        # lines[index] = substring
                        if any(line.startswith(heading) for heading in SUMMARY_OBJECTIVE_HEADINGS) and not summary_index_marked:
                        # if line in SUMMARY_OBJECTIVE_HEADINGS and not summary_index_marked:
                            summary_index = index
                            summary_index_marked = 1
                        elif any(line.startswith(heading) for heading in CONTACT_HEADINGS) and not contact_index_marked:
                        # elif line in CONTACT_HEADINGS and not contact_index_marked:
                            contact_index = index
                            contact_index_marked = 1

                        reference_marker = index
                        found_reference_marker = 1
                        break

            if found_reference_marker:
                break


        # Set index by heading
        for index, line in enumerate(lines):
            line = line.strip()
            # line = re.sub(' +', ' ', line)
            line = line.replace(":-", "").replace(":", "").replace("-", "").replace(".", "")

            if (found_reference_marker
                and not contact_index_marked
                and index > reference_marker
                and any(line.startswith(heading) for heading in CONTACT_HEADINGS)):

                contact_index = index

            if any(line.startswith(heading) for heading in custom_headings):
                if line in EXPERIENCE_HEADINGS and experience_index == -1:
                    experience_index = index
                if line in EDUCATION_HEADINGS:
                    education_index = index
                if line in SKILLS_HEADINGS:
                    skills_index = index

        end_marker = len(lines) - 1
        return (
            lines, summary_index, experience_index, education_index,
            skills_index, contact_index, end_marker
        )

    def get_location_info(self, text, recheck=False):
        location_info = list()
        (lines, summary_index, experience_index, education_index, skills_index,
            contact_index, end_marker) = self.create_paragraphs(text)

        if recheck:
            # Get the beginning and ending lines.
            for detail in lines[1: RECHECK_THRESHOLD + 1] + lines[len(lines) - RECHECK_THRESHOLD + 1:len(lines)]:
                if detail not in location_info:
                    location_info.append(detail)

            return location_info

        for index, line in enumerate(lines):
            line = line.strip()

            if summary_index != -1:
                for detail in lines[index:summary_index]:
                    if detail not in location_info:
                        location_info.append(detail)

            if contact_index != -1:
                for detail in lines[contact_index + 1:end_marker + 1]:
                    if detail not in location_info:
                        location_info.append(detail)

        return location_info

    def get_basic_experience_info(self, text, recheck=False):
        """
        Mostly, YOE is defined at starting of the resume or in summary part.

        ==================
        Expected Behaviour
        ==================
          - Create paragraphs of text of the resume.
          - For each line of the paragraphs check for the resume headings.
          - Append YOE related lines to `experience_info`.
            There might be 2 cases:
              1) If summary is available in the text then append lines containing
                 summary itself and lines before summary to `experience_info`.
              2) If summary isn't available then get the lines starting from the
                 resume to the next heading.
                 (i.e. Lines from starting to say `Experience`.)
          - If YOE couldn't found from the above then get the first few lines of
            `experience` part and append it to `experience_info`.
            `recheck` param is for that.
        """

        experience_info = list()
        index_list = list()

        # Create paragraph from given text from jarvis.resume.
        (lines, summary_index, experience_index, education_index, skills_index,
            contact_index, end_marker) = self.create_paragraphs(text)

        # List of indexes.
        index_list.extend((
            experience_index, education_index, skills_index,
            contact_index, end_marker
        ))
        index_list.sort()

        next_idx_to_summary = [i for i in index_list if i > summary_index]

        for index, line in enumerate(lines):
            line = line.strip()

            # Re-check YOE in `experience` part.
            if recheck and experience_index != -1:
                for detail in lines[experience_index: experience_index + 8]:
                    if detail not in experience_info:
                        experience_info.append(detail)

                return experience_info

            # summary_index exists.
            if summary_index != -1:
                for detail in lines[index:summary_index]:
                    if detail not in experience_info:
                        experience_info.append(detail)

                for detail in lines[summary_index:next_idx_to_summary[0]]:
                    if detail not in experience_info:
                        experience_info.append(detail)

            # summary_index doesn't exists.
            if summary_index == -1 and len(next_idx_to_summary) != 0:
                for detail in lines[index:next_idx_to_summary[0]]:
                    if detail not in experience_info:
                        experience_info.append(detail)

        return experience_info


class ExtractFeatures:
    """Extracts features like location, company names, experience from the resume text"""

    __metaclass__ = Singleton


    def __init__(self):
        # self.df_location = pd.read_csv(settings.LOCATION_NAMES)
        # self.df_company_names = pd.read_excel(settings.COMPANY_NAMES)
        # self.df_college_names = pd.read_csv(settings.INSTITUTION_NAMES)

        # self.summary_index = -1
        # self.experience_index = -1
        # self.education_index = -1
        # self.skills_index = -1
        # self.contact_index = -1

        location_qs = Location.objects.annotate(name_lower=Lower('name'))
        self.set_location = set(location_qs.values_list('name_lower', flat=True))

        company_qs = Company.objects.annotate(name_lower=Lower('name'))
        self.set_company_names = set(company_qs.values_list('name_lower', flat=True))

        college_qs = Institution.objects.annotate(name_lower=Lower('name'))
        self.set_college_names = set(college_qs.values_list('name_lower', flat=True))

    def _clean_text(self, text):
        """
        This method do simple text cleaning
        :param text: raw text
        :return: structured text
        """
        text = unidecode(text)
        text = text.replace('\n', '')
        text = text.replace('\r', '')
        text = text.replace('\t', '')
        return text

    def _text_preprocessing(self, text):
        """
        This functions apply some text processing on the resume content.
        Takes in a string of text, then performs the following:
            1. Remove all punctuation
            2. Remove all stopwords
            3. Returns a list of the cleaned text
        :return: list of cleaned text
        """
        try:
            text = self._clean_text(text).lower()
            text = text.replace("/", "").replace("-", " ")
            no_punctuation = [char for char in text if char not in string.punctuation]
            # Join the characters again to form the string.
            no_punctuation = ''.join(no_punctuation)
            # Now just remove any stopwords
            return [word for word in no_punctuation.split() if word.lower() not in stopwords.words('english')]
        except Exception as error:
            return error

    def _get_all_location(self, text):
        """
        This method do simple text matching between list_location and processed text
        :param text: processed text
        :return: list of possible location names
        """
        try:
            possible_location_names = set(text) & self.set_location
            return possible_location_names
        except Exception as error:
            return error

    def get_text_from_location_info(self, location_info):
        text = " ".join(location_info)
        text = text.replace(",", " ").replace("-", " ")

        return text

    def get_possible_location_names(self, text):
        possible_location_names = list()
        pre_processed_text = self._text_preprocessing(text)

        for loc in self.set_location:
            if loc in pre_processed_text:
                possible_location_names.append(loc)

        return possible_location_names

    def get_location(self, text):
        """
        This method uses nltk to extract location names from the processed text
        :param text: processed text
        :return: list of location names.
        """

        if not text or len(text) < 200:
            return list()

        idx_headings = IndexHeadings()

        try:
            # location_info = self.get_location_info(text)
            location_info = idx_headings.get_location_info(text)
            loc_info_text = self.get_text_from_location_info(location_info)
            possible_location_names = self.get_possible_location_names(loc_info_text)

            if len(possible_location_names) == 0:
                # location_info = self.get_location_info(text, recheck=True)
                location_info = idx_headings.get_location_info(text, recheck=True)
                loc_info_text = self.get_text_from_location_info(location_info)
                possible_location_names = self.get_possible_location_names(loc_info_text)

            return possible_location_names
        except Exception as error:
            raise error

    def get_company_names(self, text):
        """
        This method extracts company names from the preprocessed text
        :param text: processed text
        :return: list of company names.
        """
        try:
            text = self._clean_text(text)
            text = text.lower()
            possible_company_names = []
            for item in self.set_company_names:
                if item in text:
                    possible_company_names.append(item)
            return possible_company_names
        except Exception as error:
            return error

    def get_institution_names(self, text):
        """
        This method extracts college, institution names from the preprocessed text
        :param text: processed text
        :return: list of company names.
        """
        try:
            text = self._clean_text(text)
            text = text.lower()
            possible_college_names = []
            for item in self.set_college_names:
                if item in text:
                    possible_college_names.append(item)
            return possible_college_names
        except Exception as error:
            return error

    def get_dates(self, text):
        """
        This method uses nltk to extract date and its formats from the processed text
        :param text: processed text
        :return: list of location names.
        """
        try:
            text = self._clean_text(text)
            nlp = spacy.load('en')
            doc = nlp(str(text))
            possible_dates = []
            for ent in doc.ents:
                if ent.label_ == 'DATE':
                    possible_dates.append(ent.text)
            possible_dates = [dates.lower().strip() for dates in possible_dates]
            return possible_dates
        except Exception as error:
            return error

    def get_details(self, text):
        """
        This method extract features like location, company and institution names from the resume text
        :param text: resume text
        :return: dictionary of features.
        """
        features = {
            'location': self.exact_location(text),
            'company_names': self.get_company_names(text),
            'institution_names': self.get_institution_names(text)
        }
        return features

    def exact_location(self, text):
        """
        This method try to find exact location, extracting information from the top and bottom of the document
        :param text: resume text
        :return: list: list of possible location names.
        """
        try:
            first = []
            last = []
            location = self.get_location(text)
            text = self._clean_text(text)
            text = text.lower()
            first_thousand = text[:300]
            last_thousand = text[len(text)-300:]
            for item in location:
                if item in first_thousand:
                    first.append(item)
                if item in last_thousand:
                    last.append(item)
            if not last and first:
                location = first
            if not first and last:
                location = last
            if last and first:
                location = list(set(first) & set(last))
            return location
        except Exception as error:
            return error

    def _find_index(self, list_input, text):
        """
        :param: list : list of dates or companies
        :return: dictionary of index as key, list_input as value.
        """
        indexes = []
        for item in list_input:
            all_indexes = [m.start() for m in re.finditer(item, text.lower())]
            for index in all_indexes:
                indexes.append({'index': index, 'item': item})
        return indexes

    def _find_date_similarity(self, text):
        """
        This method find similar dates from the dates extracted from the text.
        :param text: string: parsed text
        :return: list: list of possible dates.
        """
        dates = self.get_dates(text)
        dates = [item.replace("(", "").strip() for item in dates]
        dates = [item.replace(")", "").strip() for item in dates]
        dates = [item.replace("*", "").strip() for item in dates]
        clean_text = self._clean_text(text).lower()
        dates_index = self._find_index(dates, clean_text)
        dates = [item for item in dates if len(item)>3]
        for date in dates_index:
            for next_date in dates_index:
                if date != next_date:
                    if abs(date['index'] - next_date['index']) <= 50:
                        start_index = date['index']
                        end_index = next_date['index'] + len(next_date['item']) + 1
                        matched_date = clean_text[start_index:end_index].strip()
                        dates.append(matched_date)
        dates = [_f for _f in dates if _f]
        return dates

    def _find_more_similarity(self, date_similarity, text):
        """
        This private method find dates similarity from the already similar dates.
        :param date_similarity: list: output of _find_date_similarity()
        :param text: list: all possible dates.
        :return:
        """
        clean_text = self._clean_text(text).lower()
        date_similarity_index = self._find_index(date_similarity, clean_text)
        dates = []
        for date in date_similarity_index:
            for next_date in date_similarity_index:
                if date != next_date:
                    if abs(date['index'] - next_date['index']) <= 50:
                        start_index = date['index']
                        end_index = next_date['index'] + len(next_date['item']) + 1
                        matched_date = clean_text[start_index:end_index].strip()
                        dates.append(matched_date)
        dates = [_f for _f in dates if _f]
        return dates

    def get_company_date(self, text):
        """
        This method extract company names with dates, time frame from the parsed text
        :param text: string - parsed text
        :return: tuple: all possible company names with dates and time frame.
        """
        try:
            clean_text = self._clean_text(text).lower()
            dates = self.get_dates(text)
            dates = [item.replace("(", "").strip() for item in dates]
            dates = [item.replace(")", "").strip() for item in dates]
            dates = [item.replace("*", "").strip() for item in dates]
            companies = self.get_company_names(text)
            dates_index = self._find_index(dates, clean_text)
            companies_index = self._find_index(companies, clean_text)
            company_dates = []
            company_similarity = []
            date_similarity = self._find_date_similarity(text)
            date_similarity = [item.translate(None, "(").strip() for item in date_similarity]
            date_similarity = [item.translate(None, ")").strip() for item in date_similarity]
            date_similarity = [item.replace("*", "").strip() for item in date_similarity]
            date_similarity_index = self._find_index(date_similarity, clean_text)
            more_similarity = []
            for date in dates_index:
                for company in companies_index:
                    if abs(company['index'] - date['index']) <= 50:
                        start_index = company['index']
                        end_index = date['index'] + len(date['item'])
                        company_name = clean_text[start_index: (start_index + len(company['item']))].strip()
                        company_date = clean_text[date['index']: end_index].strip()
                        company_dates.append({"company_name": company_name, "date": company_date})
            for date in date_similarity_index:
                for company in companies_index:
                    if abs(company['index'] - date['index']) <= 60:
                        start_index = company['index']
                        end_index = date['index'] + len(date['item'])
                        company_name = clean_text[start_index: (start_index + len(company['item']))].strip()
                        company_date = clean_text[date['index']: end_index].strip()
                        company_similarity.append({"company_name": company_name, "date": company_date})
            more_dates_similarity = self._find_more_similarity(date_similarity, text)
            more_dates_similarity = [item.translate(None, "(") for item in more_dates_similarity]
            more_dates_similarity = [item.translate(None, ")") for item in more_dates_similarity]
            more_dates_similarity_index = self._find_index(more_dates_similarity, clean_text)
            for date in more_dates_similarity_index:
                for company in companies_index:
                    if abs(company['index'] - date['index']) <= 80:
                        start_index = company['index']
                        end_index = date['index'] + len(date['item'])
                        company_name = clean_text[start_index: (start_index + len(company['item']))].strip()
                        company_date = clean_text[date['index']: end_index].strip()
                        more_similarity.append({"company_name": company_name, "date": company_date})
            possible_dates = company_dates + company_similarity + more_similarity
            all_dates = [date['date'] for date in possible_dates]
            for i in range(0, 20):
                for detail in possible_dates:
                    for item in all_dates:
                        if (detail['date'] in item) and (detail['date'] != item):
                            possible_dates.remove(detail)
                            break
            final_dates = []
            for item in possible_dates:
                final_dates.append("%s, %s" % (item['company_name'], item['date']))
            return list(set(final_dates))
            # return possible_dates
        except Exception as error:
            return error
