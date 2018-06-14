from gensim import models
from django.conf import settings

import re
model = models.Word2Vec.load(settings.SKILLS_INDEX)

def skill_match_percent(resume, skills):
    matched_skills = []
    related_skills = {}
    related_skills_in_resume = {}
    matched_related_skills = []
    percent = 0.0

    for s in skills:
        try:
            rskills = model.wv.most_similar(s)
        except Exception as e:
            continue

        if rskills and not related_skills.get(s):
            related_skills[s] = []

        related_skills[s].extend([x[0] for x in rskills])

    # total_skills = related_skills + skills

    matched_count = 0
    related_count = 0

    content = resume.content.lower()
    content = re.findall(r"[\w']+", content)

    for skill in skills:
        if skill in content:
            # direct match
            matched_skills.append(skill)
            matched_count += 1
        else:
            # check related match
            values = related_skills.get(skill, [])
            for v in values:
                if v in content:
                    if related_skills_in_resume.get(skill) is None:
                        related_skills_in_resume[skill]= []

                    related_skills_in_resume[skill].append(v)
                    related_count +=1
                    break

    ## direct match percentage
    if skills:
        percent = (float(matched_count)/len(skills)) * 100

    # related matched percentage
    if related_skills:
        percent += (float(related_count)/len(skills)) * 50

    matched_skills = set([x for x in matched_skills if x.strip()])

    for k, values in related_skills.items():
        matched_related_skills.extend(values)

    matched_related_skills = set([x for x in matched_related_skills if x.strip()])

    return percent, matched_skills, matched_related_skills, related_skills_in_resume
