from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.conf import settings

from jarvis.core.utils.common import threadify

EMAIL_DICT = {
    'parse_trial_user_resume': {
        'subject': 'Link to resume details.',
        'template': 'emails/trial_use_case_email.html',
    },
}

def _send(to, context, subject, from_email, template):
    """
    Low-level wrapper for sending mail.

    parameters:
    :to: list of to email address
    :context: context dictionary for email
    :subject: email's subject in plain text
    :from_email: from email address
    :template: HTML template file with email body
    """
    body = render_to_string(template, context)
    msg = EmailMultiAlternatives(subject, body, from_email, to)
    msg.attach_alternative(body, "text/html")
    msg.send()

def send_email_to_trial_user_with_link(
        to, context, from_email=settings.DEFAULT_FROM_EMAIL):
    """
    Sends email to trial user with link

    parameters:
    :to: list of to email address
    :from: from email address (optional)
    :context: context dictionary for email body
    """
    template = EMAIL_DICT['parse_trial_user_resume']['template']
    subject = EMAIL_DICT['parse_trial_user_resume']['subject']
    return threadify(_send, to, context, subject, from_email, template)
