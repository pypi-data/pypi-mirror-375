import logging

from django.conf import settings
from django.core.mail import send_mail


log = logging.getLogger(__name__)

def email_notify(to_email, subject, plain_text, html_message=None):
    log.debug(plain_text)
    print(plain_text)
    send_mail(
        subject,
        plain_text,
        settings.EMAIL_HOST_USER,
        (to_email,),
        html_message=html_message
    )
