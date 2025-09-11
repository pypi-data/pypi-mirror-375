import logging
import warnings

import pgpy as pgpy
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from pgpy.errors import PGPError

log = logging.getLogger(__name__)


def verify_admin_encrypted_emails():
    if not settings.DEBUG:
        for admin in settings.ADMINS:
            secure_addys = [secure[0] for secure in settings.SECURE_EMAIL]
            assert admin[1] in secure_addys, \
                "It's required that admin emails use a PGP public key"
            try:
                AdminEncryptEmailBackend.encrypt("test", admin[1])
            except CanNotEncryptException as exc:
                log.warning(f"Test encryption failed {exc}")
                raise exc


class CanNotEncryptException(Exception):
    def __init__(self, message=""):
        super().__init__(message)


class AdminEncryptEmailBackend(EmailBackend):
    """
    The class only encrypts messages that are for admin users, using PGP encryption. This process includes checking the
     emails against a specific pattern to identify them as admin emails. when an email has multiple recipients they all
     must be admins or the message IS NOT encrypted.

    [django error-reporting](https://docs.djangoproject.com/en/4.2/howto/error-reporting/#server-errors)

    In terms of email composition, only the email body is considered. Other components of an email such as attachments,
    cc, bcc, and alternatives are not permitted and are removed from the email body prior to encryption. Attachments
    and alternatives can be encrypted but, this version does not do that.

    For the behaviour to work correctly, specific settings need to be configured in settings.py of the project. These
    include updating the EMAIL_BACKEND and adding the SECURE_EMAIL configurations.

    To ensure that the configurations are correctly set, the verify_admin_encrypted_emails() function should be called
    within settings.py. This function will check that all the necessary configurations are properly set up.
    """

    @staticmethod
    def encrypt(message, to):
        warnings.filterwarnings("ignore", message="IDEA has been deprecated")
        warnings.filterwarnings("ignore", message="CAST5 has been deprecated")
        warnings.filterwarnings("ignore", message="Blowfish has been deprecated")
        key = None
        for secure in settings.SECURE_EMAIL:
            if secure[0] == to:
                key = secure[1]
        if not key:
            raise CanNotEncryptException(f"SECURE_EMAIL setting needs {to}")
        try:
            key, _ = pgpy.PGPKey.from_blob(key)
            text_message = pgpy.PGPMessage.new(message)
            x = key.encrypt(text_message)
        except (PGPError, ValueError) as exc:
            raise CanNotEncryptException(f"Exception with key: {exc}")
        return f"{x}"

    def send_messages(self, email_messages):
        try:
            hostname = settings.ALLOWED_HOSTS[0]
        except IndexError:
            hostname = "not found"

        updated_messages = []
        admin_emails = [admin[1] for admin in settings.ADMINS]
        for msg in email_messages:
            is_admin_only = set(admin_emails).issuperset(set(msg.to))
            if is_admin_only:
                for to in msg.to:
                    try:
                        body = self.encrypt(msg.body, to)
                    except CanNotEncryptException as exc:
                        body = f"PGP Encryption Failed (message body removed). {exc}"

                    # attachments, alternatives, bcc and cc not allowed with encrypted body
                    new_msg = EmailMultiAlternatives(
                        to=(to,),
                        reply_to=msg.reply_to,
                        from_email=msg.from_email,
                        subject=f"{hostname} {msg.subject}",
                        body=body,
                        headers=msg.extra_headers,
                        connection=msg.connection)
                    super().send_messages([new_msg])
            else:
                updated_messages.append(msg)

        return super().send_messages(updated_messages)
