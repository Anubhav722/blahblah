from unidecode import unidecode


class SkillMatchingScore:
    """
    Skill Matching Algorithm
    :params: Skills(Comma Separated String and Parsed Text of Resume.
    :returns: float : skill matching score.
    """
    def __init__(self, skills, text):
        self.skills = skills
        self.text = text
        self.score = 0
        self.skills_matched = []
        self.list_of_skills = []
        self.len_list_of_skills = 0
        self.len_skills_matched = 0
        self.skill_matching = {}

    def get_score(self):
        """
        Calculates Skill Matching Score: Based on the skills(string of comma separated values) entered.
        :return:
        """
        # total score 1
        self.list_of_skills = self.skills.lower().split(',')
        self.list_of_skills = set([skill.strip() for skill in self.list_of_skills if skill.strip()])
        self.list_of_skills = list(self.list_of_skills)
        self.text = unidecode(self.text.lower())
        for item in self.list_of_skills:
            if item in self.text:
                self.skills_matched.append(item)
        self.len_list_of_skills = len(self.list_of_skills)
        self.len_skills_matched = len(self.skills_matched)
        self.score = 0
        if self.len_list_of_skills > 0:
            self.score = self.len_skills_matched / float(self.len_list_of_skills)
        self.skill_matching['skill_matched'] = self.skills_matched
        self.skill_matching['skill_not_matched'] = list(set(self.list_of_skills) - set(self.skills_matched))
        self.skill_matching['score'] = self.score
        return self.skill_matching