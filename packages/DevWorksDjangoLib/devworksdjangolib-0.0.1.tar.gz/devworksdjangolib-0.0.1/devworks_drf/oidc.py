import logging
# import textwrap
from calendar import timegm
from datetime import datetime, timezone

import requests
import urllib3
from django.conf import settings as SETTINGS, settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
# from drf_spectacular.extensions import OpenApiAuthenticationExtension
from requests.exceptions import HTTPError
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from urllib3.exceptions import InsecureRequestWarning

from devworks_hydra.rest import Introspect, HydraRequestError

"""
tls termination is used on the VPC, we can't verify certs
"""
urllib3.disable_warnings((InsecureRequestWarning,))

log = logging.getLogger(__name__)
WWW_AUTHENTICATE_REALM = 'api'
AUTHENTICATE_TOKEN_TYPE = 'Bearer'


class RemoteService(authentication.BaseAuthentication):

    def authenticate_header(self, request):
        return '{} realm="{}"'.format(AUTHENTICATE_TOKEN_TYPE, WWW_AUTHENTICATE_REALM)

    def authenticate(self, request):
        token = self.get_token(request)
        if not token:
            log.debug("authenticate w/token {}".format(False))
            return None
        log.debug("authenticate w/token {}".format(True))
        return LoginService(request, token).authenticate()

    @staticmethod
    def get_token(request):
        header_value = request.META.get('HTTP_AUTHORIZATION', '')
        try:
            token_type, token = header_value.split()
        except ValueError:
            return None
        if not token_type.lower() == AUTHENTICATE_TOKEN_TYPE.lower():
            return None
        return token


class AuthService:

    def __init__(self, request, token):
        self.request = request
        self.token = token
        self.settings = {}
        self.now = timegm(datetime.now(timezone.utc).utctimetuple())
        self.update_settings()

    def update_settings(self):
        self.settings = getattr(SETTINGS, 'OIDC_AUTH', None)
        if not self.settings:
            raise Exception("Configure OIDC_AUTH values")

    def authenticate(self):
        raise NotImplementedError()

    @staticmethod
    def validate_token_type(token_type):
        if not token_type == 'Bearer':
            raise AuthenticationFailed("'Invalid Authorization. unexpected token type")

    def validate_token_audiences(self, audiences):
        msg = _('Invalid Authorization. Invalid token audience.')
        expected = self.settings['audiences']
        if len(expected) > 0:
            if not isinstance(audiences, list):
                audiences = [audiences]
            log.info("Expected {} found {}".format(expected, audiences))
            if not any(aud in expected for aud in audiences):
                raise AuthenticationFailed(msg)

    def validate_token_fresh(self, expire):
        if self.now >= expire:
            msg = _('Invalid Authorization. Token has expired.')
            raise AuthenticationFailed(msg)

    def validate_token_ready(self, not_before):
        BUFFER_SECONDS = 10
        if not_before is None:
            return
        if (self.now + BUFFER_SECONDS) <= not_before:
            msg = _('Invalid Authorization. Token not ready to start.')
            raise AuthenticationFailed(msg)

    @staticmethod
    def get_user(user_id):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(subject=user_id)
        except user_model.DoesNotExist:
            log.info("Try to access non existent user (return 401)")
            raise AuthenticationFailed("Invalid Authorization. No such user")
        log.info("user authorization: {}".format(user_id))
        return user

    @staticmethod
    def get_or_create_user(user_id, userinfo):
        groups = userinfo.get('groups', {})
        is_staff = 'staff' in groups
        is_superuser = 'superuser' in groups
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=user_id,
            defaults={
                "username": user_id,
                "is_staff": is_staff,
                "is_superuser": is_superuser
            }
        )
        if user.is_staff != is_staff or user.is_superuser != is_superuser:
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
        log.info("user authorization: {}".format(user_id))
        return user


class LoginService(AuthService):

    @property
    def admin_endpoint(self):
        return self.settings['login']['admin']

    def authenticate(self):
        token_details = self.token_details()
        return self.get_authenticated(token_details)

    def token_details(self):
        data = cache.get(self.token)
        if data:
            log.debug("cached token details found")
            return data

        error_msg = _('Invalid Authorization. Unable to verify authentication token')
        blacklisted = cache.get("blacklist" + self.token)
        if blacklisted:
            raise AuthenticationFailed(error_msg)

        try:
            introspect = Introspect()
            token_details = introspect.token(self.token)
        except (HTTPError, HydraRequestError) as exc:
            log.debug(exc)
            raise AuthenticationFailed(error_msg)
        if not token_details.get('active'):
            log.debug("token_details active false")
            raise AuthenticationFailed(error_msg)
        self.validate_token_details(token_details)
        cache.set(self.token, token_details, 5 * 60)
        return token_details

    def validate_token_details(self, token_details):
        try:
            self.validate_token_type(token_details['token_type'])
            self.validate_token_audiences(token_details['aud'])
            self.validate_token_fresh(token_details['exp'])
        except IndexError as exc:
            msg = _('Invalid Authorization. Attribute missing {}'.format(str(exc)))
            raise AuthenticationFailed(msg)
        self.validate_token_ready(token_details.get('nbf'))

    def get_authenticated(self, token_details):
        try:
            scope = token_details['scope'].split(' ')
            user_id = token_details['sub']
            audiences = token_details['aud']
            if not isinstance(audiences, list):
                audiences = [audiences]
        except IndexError as exc:
            msg = _('Invalid Authorization. Attribute missing {}'.format(str(exc)))
            raise AuthenticationFailed(msg)

        if settings.USERINFO_URL.lower() == 'local':
            return self.get_user(user_id), {
                "scope": scope,
                'aud': audiences,
                'token': self.token
            }

        userinfo = self.get_userinfo()
        return self.get_or_create_user(user_id, userinfo), {
            "scope": scope,
            'aud': audiences,
            'token': self.token
        }

    def get_userinfo(self):
        key = 'userinfo' + self.token
        cached_data = cache.get(key)
        if cached_data:
            log.debug("cached token details found")
            return cached_data
        error_msg = _('Invalid Authorization. Unable to verify authentication token')
        headers = {"Authorization": "Bearer {}".format(self.token)}
        response = requests.get(
            settings.USERINFO_URL,
            headers=headers
        )
        if response.status_code != 200:
            log.debug("{} {}".format(response.status_code, response.text))
            raise AuthenticationFailed(error_msg)

        user_data = response.json()
        cache.set('userinfo' + self.token, user_data, 5 * 60)
        return user_data
