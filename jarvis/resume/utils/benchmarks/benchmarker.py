from jarvis.resume_parser import extract_resume
import glob

path_to_resume_folder = '/home/yoda/webapps/resume-parser/jarvis/resume/utils/rsm/*'
resume_list = glob.glob(path_to_resume_folder)


fname = 0
lname = 0
phone = 0
mobile = 0
email_no = 0

skill = 0
skill_role = 0
skill_technology = 0
skill_languages = 0

workex = 0
workex_experience = 0
workex_projects = 0

education = 0
education_qual = 0

total = 0


blacklist = ["0000000000"]


def run_benchmark(quick_mode=False):
    """
    ./manage.py benchmark
    """
    global resume_list
    global fname
    global lname
    global phone
    global skill
    global workex
    global education
    global email_no
    global total
    global blacklist
    if quick_mode:
        resume_list = resume_list[:5]
    for resume in resume_list:
        response = benchmark(resume)
        total += 1
        if "basics" in list(response.keys()):
            first_name = response["basics"]["first_name"]
            last_name = response["basics"]["last_name"]
            email = response["basics"]["email"]
            phone_no = response["basics"]["last_name"]
            if len(first_name) > 0:
                fname += 1
            if len(last_name) > 0:
                lname += 1
            if len(phone_no) > 0:
                for error in blacklist:
                    if error in phone_no:
                        pass
                    else:
                        phone += 1
            if len(email) > 0:
                email_no += 1

        if "work_experience" in list(response.keys()):
            workex += 1
        if "skills" in list(response.keys()):
            skill += 1
        if "education_and_training" in list(response.keys()):
            education += 1

def benchmark(path):
    response_dict = extract_resume(path)
    return response_dict

run_benchmark(quick_mode=False)
