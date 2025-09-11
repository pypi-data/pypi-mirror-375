import base64
import json
import logging
import re
from json import JSONDecodeError
from urllib.parse import urlparse, parse_qs

import requests
import urllib3
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from requests import HTTPError
from urllib3.exceptions import InsecureRequestWarning

HEADERS_BASE = {'Content-Type': 'application/json', 'Accept': 'application/json'}
log = logging.getLogger(__name__)

"""
tls termination is used on the VPC, we can't verify certs
"""
urllib3.disable_warnings((InsecureRequestWarning,))

"""
API ref: https://github.com/ory/docs/blob/master/docs/hydra/sdk/api.md

@todo: limit/offset list results
"""


class RequestException(ValidationError):
    pass


class HydraRequestError(Exception):
    def __init__(self, message, path, raised, raw, exc=None):
        self.message = message
        self.path = path
        self.raised = raised
        self.raw = raw
        self.exc = exc


def show_request_error(res, message):
    log.warning("{}, {}, {}, {}".format(
        message,
        res.url,
        res.status_code,
        res.text[:250].replace("\n", " ")
    ))


class Base:
    @property
    def base(self):
        raise NotImplementedError()

    def __init__(self):
        self.headers = HEADERS_BASE
        if settings.HYDRA_ADMIN_TLS_TERMINATION:
            self.headers.update({"X-Forwarded-Proto": "https"})

    def path(self, part):
        log.debug("{}".format(self.base + '/' + part))
        return self.base + '/' + part

    @staticmethod
    def response_json(res):
        if res.status_code == 204:
            # no content necessary
            return
        if not res.ok:
            show_request_error(res, "failed")
            raise RequestException(code=res.status_code, message=res.text)
        return res.json()

    def _get(self, path, params=None, include_headers=False):
        try:
            res = requests.get(
                self.path(path),
                params,
                headers=self.headers,
                allow_redirects=False,
                verify=False
            )
            if include_headers:
                return self.response_json(res), res.headers
            return self.response_json(res)
        except (HTTPError, JSONDecodeError, RequestException) as exc:
            raise HydraRequestError(
                "GET '{}' failed with: {} {}".format(
                    path,
                    type(exc).__name__,
                    str(exc)
                ),
                path=path,
                raised=type(exc).__name__,
                raw=exc.args,
                exc=exc
            )

    def _put(self, path, data=None):
        try:
            data = json.dumps(data)
            res = requests.put(self.path(path), data, headers=self.headers, verify=False)
            return self.response_json(res)
        except (HTTPError, JSONDecodeError, RequestException) as exc:
            raise HydraRequestError(
                "PUT '{}' failed with: {} {}".format(
                    path,
                    type(exc).__name__,
                    str(exc)
                ),
                path=path,
                raised=type(exc).__name__,
                raw=exc.args
            )

    def _post(self, path, data):
        try:
            data = json.dumps(data)
            headers = self.headers.copy()
            res = requests.post(self.path(path), data, headers=headers, verify=False)
            return self.response_json(res)
        except (HTTPError, JSONDecodeError, RequestException) as exc:
            raise HydraRequestError(
                "POST '{}' failed with: {} {}".format(
                    path,
                    type(exc).__name__,
                    str(exc)
                ),
                path=path,
                raised=type(exc).__name__,
                raw=exc.args
            )

    def _delete(self, path):
        try:
            res = requests.delete(self.path(path), headers=self.headers, verify=False)
            return self.response_json(res)
        except (HTTPError, JSONDecodeError, RequestException) as exc:
            raise HydraRequestError(
                "DELETE '{}' failed with: {} {}".format(
                    path,
                    type(exc).__name__,
                    str(exc)
                ),
                path=path,
                raised=type(exc).__name__,
                raw=exc.args
            )


class Public(Base):

    @property
    def base(self):
        return settings.HYDRA_PUBLIC_URL

    def auth(self, params):
        return self._get('oauth2/auth', params)

    def token(self, params):
        return self._get('oauth2/token', params)


class Discovery(Base):
    @property
    def base(self):
        return settings.HYDRA_PUBLIC_URL

    def openid_connect(self):
        return self._get('.well-known/openid-configuration')

    def json_web_keys(self):
        return self._get('.well-known/jwks.json')


class Private(Base):
    @property
    def base(self):
        return settings.HYDRA_ADMIN_URL

    def version(self):
        return self._get('version')


class Clients(Base):
    @property
    def base(self):
        return settings.HYDRA_ADMIN_URL

    def all(self, **kwargs):

        def extract_next_page_token(header):
            pattern = r'<([^>]+)>;\s*rel="next"'
            match = re.search(pattern, header)
            if match:
                next_url = match.group(1)
                parsed_url = urlparse(next_url)
                query_params = parse_qs(parsed_url.query)
                return query_params.get('page_token', [None])[0]
            return None

        params = {
            "page_size": 250,
            "page_token": 1,
            **kwargs
        }

        while True:
            clients, headers = self._get(
                'admin/clients',
                params,
                include_headers=True
            )

            next = extract_next_page_token(headers['Link'])
            for client in clients:
                yield client
            if not clients:
                break
            if not next:
                break
            params['page_token'] = next

    def create(self, data):
        return self._post('admin/clients', data)

    def get(self, client_id):
        return self._get(f'admin/clients/{client_id}')

    def update(self, client_id, data):
        return self._put(f'admin/clients/{client_id}', data)

    def delete(self, client_id):
        return self._delete(f'admin/clients/{client_id}')


class Login(Base):
    @property
    def base(self):
        return settings.HYDRA_ADMIN_URL

    def get(self, challenge):
        return self._get(
            'admin/oauth2/auth/requests/login?login_challenge={}'.format(challenge)
        )

    def accept(self, challenge, data):
        return self._put(
            'admin/oauth2/auth/requests/login/accept?login_challenge={}'.format(challenge),
            data
        )

    def reject(self, challenge, data):
        return self._put(
            'admin/oauth2/auth/requests/login/reject?login_challenge={}'.format(challenge),
            data
        )


class Consent(Base):
    @property
    def base(self):
        return settings.HYDRA_ADMIN_URL

    def get(self, challenge):
        return self._get(
            'admin/oauth2/auth/requests/consent?consent_challenge={}'.format(challenge)
        )

    def accept(self, challenge, data):
        return self._put(
            'admin/oauth2/auth/requests/consent/accept?consent_challenge={}'.format(challenge),
            data
        )

    def reject(self, challenge):
        return self._put(
            'admin/oauth2/auth/requests/consent/reject?consent_challenge={}'.format(challenge)
        )

    def revoke(self, user):
        return self._delete(
            'oauth2/auth/sessions/consent?subject={}'.format(user)
        )


class Logout(Base):
    @property
    def base(self):
        return settings.HYDRA_ADMIN_URL

    def get(self, challenge):
        return self._get(
            'admin/oauth2/auth/requests/logout?logout_challenge={}'.format(challenge)
        )

    def accept(self, challenge):
        return self._put(
            "admin/oauth2/auth/requests/logout/accept?logout_challenge={}".format(challenge)
        )

    def force(self, user):
        return self._delete(
            'admin/oauth2/auth/sessions/login?subject={}'.format(user)
        )


class Session(Base):
    @property
    def base(self):
        return settings.HYDRA_ADMIN_URL

    def list(self, user):
        return self._get(
            'admin/oauth2/auth/sessions/consent?subject={}'.format(user)
        )

    def clear(self, user):
        if user.endswith('&all=true'):
            # dirty hack here on client end to support v1
            return self._delete(
                'admin/oauth2/auth/sessions/consent?subject={}'.format(user)
            )
        return self._delete(
            'admin/oauth2/auth/sessions/consent?subject={}&all=true'.format(user)
        )


class Introspect(Base):
    @property
    def base(self):
        return settings.HYDRA_ADMIN_URL

    def token(self, token):
        headers = self.headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        path = 'admin/oauth2/introspect'
        data = {'token': token}
        try:
            res = requests.post(self.path(path), data, headers=headers, verify=False)
            return self.response_json(res)
        except (HTTPError, JSONDecodeError, RequestException) as exc:
            raise HydraRequestError(
                "POST '{}' failed with: {} {}".format(
                    path,
                    type(exc).__name__,
                    str(exc)
                ),
                path=path,
                raised=type(exc).__name__,
                raw=exc.args
            )


def make_baisc(subject, secret):
    return base64.b64encode(
        "{}:{}".format(subject, secret).encode('ascii')
    ).decode('ascii')


class MachineToken(Base):
    @property
    def base(self):
        return settings.HYDRA_PUBLIC_URL

    def get(self, subject, secret, refresh=None):
        basic_auth = make_baisc(subject, secret)
        cache_key = "machine_{}".format(basic_auth)
        token = cache.get(cache_key)
        if token and refresh is None:
            return token

        headers = self.headers.copy()
        headers["Authorization"] = "Basic {}".format(basic_auth)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        path = 'oauth2/token'
        data = {
            "client_id": subject,
            "audience": "development",
            "scope": "openid",
            "grant_type": "client_credentials"
        }

        try:
            res = requests.post(self.path(path), data, headers=headers, verify=False)
            res_json = self.response_json(res)
            token = res_json["access_token"]
            ttl_remains = res_json["expires_in"] - (5 * 60)
            cache.set(cache_key, token, ttl_remains)
            return token
        except (HTTPError, JSONDecodeError, RequestException) as exc:
            raise HydraRequestError(
                "POST '{}' failed with: {} {}".format(
                    path,
                    type(exc).__name__,
                    str(exc)
                ),
                path=path,
                raised=type(exc).__name__,
                raw=exc.args
            )
