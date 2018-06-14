from .extractor import get_text, get_text_via_ocr, verify_quality_text
from .parser_helper import get_email, get_nums, get_name, get_username_from_github_url, get_github, get_linkedin, get_id_from_linkedin_url
ocr_flag = False


def parser(path_to_pdf):
    global ocr_flag
    parsed_text = run_extractor(path_to_pdf)
    if parsed_text is not None:
        """
        PARSER EXTRACTION PHASE
        """
        emails = get_email(parsed_text.lower())
        if emails is None:
            parsed_text = run_ocr(path_to_pdf)
            if parsed_text is None:
                return None
            emails = get_email(parsed_text.lower())
            ocr_flag = True

        name = get_name(parsed_text.lower())
        if (name is None) and (not ocr_flag):
            parsed_text = run_ocr(path_to_pdf)
            if parsed_text is None:
                return None
            name = get_name(parsed_text.lower())
            ocr_flag = True

        mobiles = get_nums(parsed_text.lower())

        """
        BUILD DEFAULT RESPONSE OBJECT TO AVOID KEY ERRORS
        """
        candidate_info = dict()
        candidate_info['github_user'] = ""
        candidate_info['github_url'] = ""
        candidate_info['names'] = ""
        candidate_info['emails'] = ""
        candidate_info['phones'] = ""
        candidate_info['linkedin_user'] = ""
        candidate_info['linkedin_url'] = ""

        """
        GITHUB & LINKEDIN SECTION
        """
        github_urls = get_github(parsed_text.lower())
        if github_urls is not None:
            candidate_info['github_url'] = list(set(github_urls))
            github_user = get_username_from_github_url(parsed_text.lower())
            if github_user is not None:
                candidate_info['github_user'] = github_user

        linkedin_urls = get_linkedin(parsed_text.lower())
        if linkedin_urls is not None:
            candidate_info['linkedin_url'] = list(set(linkedin_urls))
            linkedin_user = get_id_from_linkedin_url(parsed_text.lower())
            if linkedin_user is not None:
                candidate_info['linkedin_user'] = linkedin_user
        """
        NAME SECTION
        """
        name = blacklist_scrubber(name)
        if (name is not None) and (len(name) > 0):
            candidate_info['names'] = list(set(name))

        else:
            alt_name = get_alternative_name(
                candidate_info["linkedin_user"], candidate_info["github_user"])
            if alt_name is not None:
                candidate_info['names'] = [alt_name]
            else:
                candidate_info['names'] = ''

        if emails is not None:
            candidate_info['emails'] = emails
        else:

            candidate_info['emails'] = ''
        if mobiles is not None:
            candidate_info['phones'] = mobiles
        else:
            candidate_info['phones'] = ''
        candidate_info['parsed_text'] = parsed_text

        return candidate_info

    else:
        return None


def run_extractor(path_to_pdf):
    global ocr_flag
    text = get_text(path_to_pdf)
    if text is None:
        text = " "
    return text

    '''
    if verify_quality_text(parsed_text):
        return parsed_text
    else:
        ocr_parsed_text = get_text_via_ocr(path_to_pdf)
        return ocr_parsed_text
    '''


def run_ocr(path_to_pdf):
    text = get_text_via_ocr(path_to_pdf)
    return text


def get_alternative_name(linkedin, github):
    if len(linkedin) > 0:
        return linkedin
    elif len(github) > 0:
        return github
    else:
        return None


def blacklist_scrubber(name_list):
    blacklist = ['contact', 'info']
    if name_list is None:
        return name_list
    for name in name_list:
        if name in blacklist:
            name_list.remove(name)
    return name_list
