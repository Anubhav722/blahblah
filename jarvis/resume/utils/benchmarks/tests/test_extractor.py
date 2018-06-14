from extractor import get_text, get_text_via_ocr, verify_quality_text
import glob
from parser_helper import compare_email_line, get_name, get_nums, get_email, get_name_data_from_email, get_name_candidates_from_email
path_to_resume_folder = '/home/launchyard/Work/parser/resume-parser/jarvis/docx/*.pdf'
resume_list = glob.glob(path_to_resume_folder)
well_formed = 0
malformed = 0
no_phone = 0
no_mail = 0
no_name = 0
name_match = 0


def parse(pdf):
    global name_match
    global no_mail
    global no_name
    global well_formed
    global no_phone
    text = get_text(pdf)
    if verify_quality_text(text):
        well_formed = well_formed + 1
        phone_number = get_nums(text)
        mail = get_email(text)
        if mail != None:
            # print get_name_data_from_email(text)
            matches = get_name(text.lower())
            if matches is None:
                first_line = text.split('\n')[0]
                match = compare_email_line(text.lower(), first_line)
                if not match:
                    no_name = no_name + 1
                else:
                    print(first_line)
                    name_match = name_match + 1

            else:
                name_match = name_match + 1
                print(matches)
        else:
            no_mail = no_mail + 1
           # print text
        if phone_number is None:
            no_phone = no_phone + 1

    '''
    else:
        text = get_text_via_ocr(pdf)
        if verify_quality_text(text):

            phone_number = get_nums(text)
            mail = get_email(text)
            if mail != None:
               # print get_name_data_from_email(text)
                name_matcher(text)
            else:
                no_mail = +1
                if phone_number is None:
                    no_phone = +1
        else:
            malformed = malformed + 1
    '''
for pdf in resume_list:
    parse(pdf)
# parse('resume.pdf')
print(("Malformed Pdf = " + str(malformed)))
print(("Well_formed=" + str(well_formed)))
print(("No phone = ") + str(no_phone))
print(("No mail = ") + str(no_mail))
print(("name match=") + str(name_match))
print(("No name match=") + str(no_name))
