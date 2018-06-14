# External Imports
import io
import os
import re
from .features import IndexHeadings
from .constants import YEAR_REGEX, MONTH_REGEX
from unidecode import unidecode
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from pandas import DataFrame
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from nltk.tokenize import sent_tokenize, word_tokenize
from heapq import nlargest
from collections import defaultdict

# Regex to extract number of experience from text.
# REGEX_EXPERIENCE = r"[-+]?\d*\.\d+|\d+"
REGEX_EXPERIENCE = r"(0[1-9]|1[0-9]|2[0]|\d{1})(\.[0-9]|1[0-9]?)?"

def get_tokens(text):
    """
    This function cleans up, remove stop words and extracts tokens from the
    parsed text obtained from the resume.
    :param text: parsed text from jarvis.resume.
    :return: list of tokens
    """
    text = unidecode(text)
    # removing new lines from the decoded text
    text = text.replace('\n', '')
    tokens = word_tokenize(text)

    return tokens


def remove_stop_words(tokens):
    """
    This function takes list of tokens as an input and remove
    unnecessary or stop words.
    :param tokens: list
    :return: list
    """
    stop_words = set(stopwords.words('english'))
    filtered_text = [w for w in tokens if w not in stop_words]
    return filtered_text


def remove_punctuation(text):
    """
    This function tokenize words as well remove punctuation from the text
    :param text: parsed text from the resume
    :return: list
    """
    text = unidecode(text)
    text = text.replace('\n', '')
    # tokenize and removing punctuation
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    return tokens


# converting all resumes to text format and saving them as test and
# trained data

class FeatureExtraction:
    """
    Find the Frequency of words occurring in a text document and summarize them on the basis of frequency.
    """
    def __init__(self, min_cut=0.1, max_cut=0.9):
        self._min_cut = min_cut
        self._max_cut = max_cut
        self._stop_words = set(stopwords.words('english'))
        self._freq = 0

    def _compute_frequencies(self, word_sent, custom_stop_words=None):
        freq = defaultdict(int)
        stop_words = set(self._stop_words)
        if custom_stop_words is not None:
            stop_words = set(custom_stop_words).union(self._stop_words)

        for sentence in word_sent:
            for word in sentence:
                if word not in stop_words and word != '':
                    freq[word] += 1
        m = float(max(freq.values()))
        for word in list(freq.keys()):
            freq[word] /= m
            if freq[word] >= self._max_cut or freq[word] <= self._min_cut:
                del freq[word]
        return freq

    def summarize(self, text, n):
        """
        Summarize the text.
        :param text: parsed text from jarvis.resume
        :param n: threshold value of frequency
        :return: summary of the text
        """
        sentences = sent_tokenize(text)
        word_sent = [word_tokenize(s.lower()) for s in sentences]

        self._freq = self._compute_frequencies(word_sent)
        ranking = defaultdict(int)
        for i, sentence in enumerate(word_sent):
            for word in sentence:
                if word in self._freq:
                    ranking[i] += self._freq[word]

        sentences_index = nlargest(n, ranking, key=ranking.get)
        return [sentences[j] for j in sentences_index]

    def get_year_of_experience(self, experience_info):
        """
        Get the final value containing YOE.

        ==================
        Expected Behaviour
        ==================
          - Get the YOE from sentences.
            (i.e. experience_info param that might contain YOE.)
          - Return YOE if found, otherwise None.
        """
        yoe = None
        year_exp = None   # Value the contains `YEAR` part of work experience.
        month_exp = None  # Value the contains `MONTH` part of work experience.
        sentence_with_exp = ''
        is_year_exp_avail = False
        is_month_exp_avail = False
        is_year_month_exp_avail = False

        # Check for work experience in each sentence.
        for sentence in experience_info:

            # Get the Year(s) from experience sentence.
            year_exp_result = re.search(YEAR_REGEX, sentence)
            if year_exp_result:
                # Added to check if experience (Year + Month) is from
                # same line or not, afterwards.
                sentence_with_exp = sentence
                year_exp_text = year_exp_result.group()
                year_result = re.search(r'\d*\s*?\.?\s*?\d+', year_exp_text)
                if year_result:
                    # Digit (<type 'str'>) containing `YEAR` value.
                    year_exp = year_result.group().replace(" ", "")

            # Get the Month(s) from experience sentence.
            month_exp_result = re.search(MONTH_REGEX, sentence)
            if month_exp_result:
                # String containing .
                month_exp_text = month_exp_result.group()
                month_result = re.search(r'\d+', month_exp_text)
                if month_result:
                    # Digit (<type 'str'>) containing `MONTH` value.
                    month_exp = month_result.group()

            # If both `YEAR` and `MONTH` are in YOE.
            if year_exp and month_exp and not is_year_month_exp_avail and sentence == sentence_with_exp:
                yoe = float(year_exp) + (float(month_exp) / 12.00)
                yoe = float("{0:.1f}".format(yoe))
                is_year_month_exp_avail = True

            # If only `YEAR` is in YOE.
            if year_exp and not month_exp and not is_year_exp_avail:
                yoe = float(year_exp); is_year_exp_avail = True
                # if yoe > 20:
                #     yoe = 0.0; year_exp = None; is_year_exp_avail = False

            # If only `MONTH` is in YOE.
            if month_exp and not year_exp and not is_month_exp_avail:
                yoe = float(month_exp) / 12.00
                yoe = float("{0:.1f}".format(yoe))
                is_month_exp_avail = True

        return yoe

    def work_experience_extraction(self, text):
        """
        This function serve the purpose only to get the basic YOE part.
        (i.e. "Over 2+ years of experience in web applications.")
        YOE should be `2.0`.

        ==================
        Expected Behaviour
        ==================
          - Get the sentences that might contain YOE part from the text param.
          - Get the actual YOE from that sentences.
          - Return YOE.
        """

        if not text or len(text) < 200:
            return None

        idx_headings = IndexHeadings()
        experience_info = idx_headings.get_basic_experience_info(text)
        yoe = self.get_year_of_experience(experience_info)

        if yoe == 0:
            experience_info = idx_headings.get_basic_experience_info(text, recheck=True)
            yoe = self.get_year_of_experience(experience_info)

        return yoe

    def get_work_experience(self, text):
        """
        Finds the work experience from jarvis.resume.
        :param text: parsed text from jarvis.resume
        :return: string, if work experience is found. otherwise None.
        """
        # text = unidecode(text).replace('\n', '').lower()
        # text = text.replace('\r', '')
        # text = text.replace('\t', '')
        # experience = None
        # try:
        #     years_index = text.find('years')
        #     if years_index != -1:
        #         experience = text[years_index-4:years_index-1].strip()
        #         if type(float(experience)) != float:
        #             experience = text[years_index-1:years_index].strip()
        #             if type(float(experience)) != float:
        #                 sentence = text[years_index-20:years_index+30]
        #                 experience = extract_experience(REGEX_EXPERIENCE, sentence)
        #                 if type(float(experience)) != float:
        #                     experience = None
        #         else:
        #             sentence = text[years_index - 20:years_index + 30]
        #             experience = extract_experience(REGEX_EXPERIENCE, sentence)
        #     else:
        #         years_index = text.find('year')
        #         if text[years_index + 8:years_index + 18].strip() == 'experience':
        #             if years_index != -1:
        #                 experience = text[years_index - 4:years_index - 1].strip()
        #                 experience = extract_experience(REGEX_EXPERIENCE, experience)
        # except:
        #     years_index = text.find('years')
        #     sentence = text[years_index - 20:years_index + 30].strip()
        #     experience = extract_experience(REGEX_EXPERIENCE, sentence)
        # months_experience = self.get_months(text)
        #
        # if months_experience is not None and experience is None:
        #     try:
        #         experience = float(months_experience)/12.0
        #     except:
        #         return None
        #     if experience < 1:
        #         experience = 1

        # Get the work experience.
        experience = self.work_experience_extraction(text)
        if experience <= 0 or experience > 15:
            experience = None

        return experience
