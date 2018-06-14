# Django Imports
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth.models import User

# App Imports
from .models import Visitor
from django.core.exceptions import SuspiciousOperation

# Miscellaneous
import json

def store_visitor_activity(function):
    def wrap(request, *args, **kwargs):

        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if auth == '':
            raise SuspiciousOperation("No auth token provided.")
        auth_token = auth.split('Token ')[1]

        ip = get_visitor_ip(request.META)
        referer = request.META.get('HTTP_REFERER', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        method = request.method
        pageview = request.path
        query_string = json.dumps(request.GET)

        try:
            user = User.objects.get(auth_token=auth_token)
        except User.DoesNotExist:
            raise SuspiciousOperation("User does not exist.")

        # Save Visitor Details
        save_visitor_activity(
            user, ip, referer, user_agent, method, pageview, query_string
        )

        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def get_visitor_ip(request_meta):
    ip = ''
    x_forwarded_for = request_meta.get('HTTP_X_FORWARDED_FOR', "")
    x_real_ip = request_meta.get('HTTP_X_REAL_IP', "")
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    elif x_real_ip:
        ip = x_real_ip
    else:
        ip = request_meta.get('REMOTE_ADDR', "")
    return ip

def save_visitor_activity(user, ip, referer, user_agent, method, pageview, query_string):

    visitor = Visitor.objects.create(
        user=user, ip_address=ip, query_string=query_string,
        last_active=timezone.now(), referer=referer, user_agent=user_agent,
        pageview=pageview, method=method
    )

    try:
        visitor.save()
    except IntegrityError as e:
        print(("An error occurs while creation of visitor instance. Error: ", e))
        pass
