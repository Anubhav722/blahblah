
RECHECK_THRESHOLD = 10

# YEAR_REGEX = r'([a-z()]+)?\d*[.]?\d+(?:[+]?)(?:\s(yr|yrs|year|years))'
YEAR_REGEX = r'([a-z()]+)?(\d{1,2}\s*?\.\s*?)?\d{1,2}(?:\s*?[+]?)(?:\s?(yr|yrs|year|years|exp|exp.|experience))'
# YEAR_REGEX = r'([a-z()]+)?((?:[2-9]|1[0-9]|2[0]?)\.)?(?:[2-9]|1[0-9]|2[0]?)(?:[+]?)(?:\s(yr|yrs|year|years|exp|exp.|experience))'
MONTH_REGEX = r'([a-z()]+)?\d+(?:[+]?)(?:\s(month|months))'

SUMMARY_OBJECTIVE_HEADINGS = (
    "objective",
    "objectives",
    "summary",
    "overview",
    "profile",
    "profile summary",
    "about me",
    "objective/vision",
    "career summary",
    "career objective",
    "career highlights",
    "functional summary",
    "summary of qualifications",
)

EXPERIENCE_HEADINGS = (
    "experience",
    "experience summary",
    "summary of experience",
    "employers",
    "employment",
    "projects",
    "project work",
    "project profile",
    "project profiles",
    "project details",
    "projects summary",
    "project experience",
    "internships and projects",
    "projects undertaken",
    "work summary",
    "work experience",
    "work-experience",
    "personal projects",
    "employment details",
    "employment summary",
    "employment history",
    "relevant experience",
    "professional span",
    "professional details",
    "professional summary",
    "professional synopsis",
    "technical experience",
    "professional experience",
    "professional achievements",
    "professional qualification",
    "professional qualifications",
)

EDUCATION_HEADINGS = (
    "degrees",
    "academia",
    "academics",
    "academic details",
    "academic qualification",
    "academic qualifications",
    "education",
    "educations",
    "education summary",
    "education details",
    "education qualification",
    "education qualifications",
    "educational details",
    "educational qualification",
    "educational qualifications",
)

SKILLS_HEADINGS = (
    "skills",
    "skill set",
    "technologies",
    "primary skills",
    "technical skill",
    "technical skills",
    "software skills",
    "functional skills",
    "programming skills",
    "skills & expertise",
    "technology skill set",
    "technical proficiency",
    "it skills & proficiency",
    "technical skills summary",
)

CONTACT_HEADINGS = (
    # "contact",
    "about & contact",
    "my details",
    "contact details",
    "personal info",
    "personal details",
    "personal profile",
    "personal dossier",
    "personnel details",
    "personal information",
)
