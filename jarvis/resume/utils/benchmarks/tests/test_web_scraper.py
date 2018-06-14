from extractor import get_text, get_text_via_ocr
from parser_helper import get_linkedin, get_github
from url_cleaner import get_id_from_linkedin_url, yobot, get_username_from_github_url
import glob


path_pdf_folder = '/home/launchyard_kekre/code/Parser/rsm/*.pdf'
resume_list = glob.glob()
# resume_list = ['--resume.pdf']


def linkedin():
    for resume in resume_list:
        parsed_text = get_text(resume)
        linkedin = get_linkedin(parsed_text)
        if linkedin:
            print (linkedin)
            get_id_from_linkedin_url(linkedin)


def github():
    for resume in resume_list:
        parsed_text = get_text(resume)
        # print parsed_text
        github = get_github(parsed_text)
        if github:
            print((get_username_from_github_url(github)))
            pass
github()
