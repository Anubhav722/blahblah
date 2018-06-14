import re
import os
import json
import string
from .parser import parser
from subprocess import PIPE, Popen

##########################################
# Stanford Library paths, kept here so that it's easier to swap libs
# Keep this uncommented when benchmarking with out benchmark management command
# RESUME_TRANSDUCER_PATH = "/home/yoda/webapps/ResumeParser/ResumeTransducer"
# GATEFILES_PATH = "/home/yoda/webapps/ResumeParser/GATEFiles"
# STANFORD_MODELS_PATH = "/home/yoda/webapps/cvParser/cvParser/stanford-ner-2014-10-26/classifiers/english.all.3class.distsim.crf.ser.gz"
# STANFORD_NER_JAR_PATH = "/home/yoda/webapps/cvParser/cvParser/stanford-ner-2014-10-26/stanford-ner.jar"
###########################################

PHONE_REG = r'(?:\+?\d{2}[ -]?)?\d{10,11}'  # basically indian

def extract_resume(resume_path):
    secondary_dict = parser(resume_path)
    fname = ''
    lname = ''
    phones = ''
    emails = ''
    github_user = ''
    linkedin_url = ''
    github_url = ''
    linkedin_user = ''
    if secondary_dict is not None:
        text = secondary_dict['parsed_text']
        name = secondary_dict['names']
        phones = secondary_dict['phones']
        emails = secondary_dict['emails']
        github_url = secondary_dict['github_url']
        github_user = secondary_dict['github_user']
        linkedin_url = secondary_dict['linkedin_url']
        linkedin_user = secondary_dict['linkedin_user']

        if len(name) == 2:
            fname = name[0]
            lname = name[1]
        elif len(name) == 1:
            fname = name[0]
            lname = ''
        elif len(name) > 2:
            fname = name[0]
            lname = ''
            for namestring in name[1:]:
                lname = lname + " " + namestring
        else:
            fname = ''
            lname = ''
    else:
        fname = ''
        lname = ''
        emails = ''
        phones = ''

    json_file = parse_text(resume_path)
    j = open(json_file)
    s = j.read()
    if not s:
        s = '{}'

    candidate_dict = json.loads(s)
    if fname:
        fname = trim_non_alpha(fname)
    if lname:
        lname = trim_non_alpha(lname)
    if emails:
        emails = [trim_non_alpha(x) for x in emails]

    # basic_dict = candidate_dict["basics"]
    if "basics" in list(candidate_dict.keys()):
        candidate_dict["basics"]["first_name"] = fname
        candidate_dict["basics"]["last_name"] = lname
        candidate_dict["basics"]["phone"] = phones
        candidate_dict["basics"]["email"] = emails
        candidate_dict["basics"]["github_url"] = github_url
        candidate_dict["basics"]["github_username"] = github_user
        candidate_dict["basics"]["linkedin_url"] = linkedin_url
        candidate_dict["basics"]["linkedin_username"] = linkedin_user
        return candidate_dict
    else:
        candidate_details = dict()
        candidate_details["github_url"] = github_url
        candidate_details["github_username"] = github_user
        candidate_details["linkedin_url"] = github_url
        candidate_details["linkedin_username"] = github_user
        candidate_details["first_name"] = fname
        candidate_details["last_name"] = lname

        candidate_details["phone"] = phones
        candidate_details["email"] = emails
        new_candidate_dict = dict()
        new_candidate_dict["basics"] = candidate_details
        return new_candidate_dict

    return candidate_dict


def get_candidate_phone_numbers(text):
    numbers = re.findall(PHONE_REG, text)
    numbers = [x.replace("-", "") for x in numbers if len(x) >= 10]
    return numbers


def get_plain_text(resume_path):
    cmd = ["docconv", "-input", resume_path]
    p = Popen(cmd, stdout=PIPE)
    stdout, stderr = p.communicate()
    return stdout.decode('ascii', 'ignore')


def parse_text(resume_path):
    json_file = open("output.json", "w")
    # class_path = "%s/bin/*:%s/lib/*:%s/bin/gate.jar:%s/lib/*" % (
    #     settings.RESUME_TRANSDUCER_PATH, settings.GATEFILES_PATH,
    #     settings.GATEFILES_PATH, settings.RESUME_TRANSDUCER_PATH)

    # NOTE:
    # For now came up with this solution. Need to find better alternative.
    cmd = 'bash resumeparserprogram.sh {} {}'.format(resume_path, json_file.name)
    os.system(cmd)

    # rp_path = os.path.join(settings.BASE_DIR, '/ResumeParser/ResumeTransducer/')

    # cmd = ["java", "-cp", class_path,
    #        "code4goal.antony.resumeparser.ResumeParserProgram", resume_path, json_file.name]
    # p = Popen(cmd, stdout=PIPE)
    # stdout, stderr = p.communicate()
    json_file.close()
    return json_file.name

def trim_non_alpha(s):
    if not s:
        return s
    s = s.decode().encode('utf-8')
    allchars = string.maketrans('', '')
    nonchars = allchars.translate(allchars, string.letters + string.digits)
    return s.strip(nonchars)
