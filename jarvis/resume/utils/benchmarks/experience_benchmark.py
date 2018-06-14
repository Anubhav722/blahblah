from jarvis.resume.utils.machine_learning.helper import FeatureExtraction
from jarvis.resume.utils.extractor import get_text
import os

path = '~/Work/parser/filter-api/jarvis/docs'


def benchmark():
    result = {}
    features = FeatureExtraction()
    for root, dir_names, file_names in os.walk(path):
        for file_name in file_names:
            name = os.path.join(root, file_name)
            text = get_text(name)
            experience = features.get_work_experience(text)
            result[file_name] = experience

    return result
