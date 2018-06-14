from jarvis.resume.utils.resume_parser import extract_resume
import glob
from jarvis.resume.utils.extractor import get_text, stackoverflow_user_details, github_user_details
from jarvis.resume.utils.parser_helper import get_stackoverflow_userid, get_github_username, get_stackoverflow_username, url_categorizer, get_urls, url_summary
import json
from itertools import chain
import csv


path_to_resume_folder = '/home/launchyard/Work/parser/resume-parser/jarvis/docx/tested/*.pdf'
resume_list = glob.glob(path_to_resume_folder)


def benchmark(quick_mode=False):
    global resume_list
    user = {}
    if quick_mode:
        resume_list = resume_list[:5]
    for resume in resume_list:
        response = extract_resume(resume)
        # github_username = get_github_username(text)
        # stackoverflow_userid = get_stackoverflow_userid(text)
        # stackoverflow_username = get_stackoverflow_username(text)
        # stack_user_details = {}
        # git_user_details = {}
        # repo_details = {}
        # if stackoverflow_userid is None:
        #     pass
        # else:
        #     stack_user_details = stackoverflow_user_details(stackoverflow_userid)
        # if github_username is None:
        #     pass
        # else:
        #     git_user_details = github_user_details(github_username)
        #     repo_details = git_user_details['repo_details']
        # github_url =
        text = get_text(resume)
        if text is None:
            pass
        else:
            urls = get_urls(text)
            categories = url_categorizer(urls, text)
        file_name = resume
        blog = ' '
        personal_website = ' '
        github_url = ' '
        stackoverflow_url = ' '
        linkedin_url = ' '
        bit_bucket = ' '
        gist_url = ' '
        other_urls = ' '

        if 'Blog' in list(categories['Websites'].keys()):
            blog = categories['Websites']['Blog']
        if 'Personal Website' in list(categories['Websites']['Personal Urls'].keys()):
            personal_website = categories['Websites']['Personal Urls']['Personal Website']
        if 'Other Urls' in list(categories['Websites']['Personal Urls'].keys()):
            other_urls = categories['Websites']['Personal Urls']['Other Urls']
        if 'GitHub Url' in list(categories['Social Websites'].keys()):
            github_url = categories['Social Websites']['GitHub Url']
        if 'StackOverflow Url' in list(categories['Social Websites'].keys()):
            stackoverflow_url = categories['Social Websites']['StackOverflow Url']
        if 'LinkedIn Url' in list(categories['Social Websites'].keys()):
            linkedin_url = categories['Social Websites']['LinkedIn Url']
        if 'BitBucket Url' in list(categories['Social Websites'].keys()):
            bit_bucket = categories['Social Websites']['BitBucket Url']
        if 'GitHub Gist Url' in list(categories['Social Websites'].keys()):
            gist_url = categories['Social Websites']['GitHub Gist Url']
        # social = {}
        # social = {'url_categories': categories}
        # # user['Basic'] = response
        # # user['Social'] = social
        # data = {'Basic': response, 'Social': social}
        # details = dict(chain(user.items(), data.items()))
        field_names = ['file_name', 'Personal Website', 'Blog', 'GitHub', 'LinkedIn', 'StackOverflow', 'BitBucket', 'GitHub_Gist', 'Other urls']
        with open('output.csv', 'a') as csvfile:
            write = csv.DictWriter(csvfile, fieldnames=field_names)
            write.writeheader()
            write.writerow({'file_name': file_name, 'Personal Website': personal_website, 'Blog': blog, 'GitHub': github_url,
                            'LinkedIn': linkedin_url, 'StackOverflow': stackoverflow_url, 'BitBucket': bit_bucket,
                            'GitHub_Gist': gist_url, 'Other urls': other_urls})
        csvfile.close()
    # with open('json-out.json', 'w') as outfile:
    #     json.dump(details, outfile)

    return json.dumps(user)

