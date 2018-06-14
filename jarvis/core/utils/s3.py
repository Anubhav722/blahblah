from jarvis.resume.models import Resume


def get_file_name(file_name):
    instance = Resume.objects.filter(resume_location=file_name)
    return instance.file_name
