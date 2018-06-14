import os
from gensim import models

from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics

class RelatedSkills(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        model = models.Word2Vec.load(settings.SKILLS_INDEX)
        skills = request.GET.getlist('skills')
        related = []
        message = "success"
        skills = [skill.lower() for skill in skills]
        if skills:
            try:
                related = model.wv.most_similar(positive=skills)
            except KeyError:
                message= "skill not matched. forgot full name?"

        related = [x[0] for x in related]
        return Response({'related': related, 'message': message})
