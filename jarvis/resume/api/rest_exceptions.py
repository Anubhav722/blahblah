import math
from django.utils.encoding import force_text
from rest_framework import exceptions
from rest_framework.views import exception_handler


class CustomThrottled(exceptions.Throttled):
    def __init__(self, wait=None, detail=None, throttle_instance=None):
        self.throttle_instance = throttle_instance

        if detail is not None:
            self.detail = force_text(detail)
        else:
            self.detail = force_text(self.default_detail)

        if wait is None:
            self.wait = None
        else:
            self.wait = math.ceil(wait)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, CustomThrottled):  # check that a CustomThrottled exception is raised
        custom_response_data = {  # prepare custom response data
            'message': exc.detail,
            'availableIn': '%d seconds' % exc.wait,
            'throttleType': type(exc.throttle_instance).__name__
        }
        response.data = custom_response_data  # set the custom response data on response object

    return response

