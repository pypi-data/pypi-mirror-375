import logging

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now

log = logging.getLogger(__name__)

"""
THIS ALSO LOOKS ACCOUNT SERVICE SPEFICIC
"""


def redirect_to_password_change(request, password_change_url):
    response = HttpResponseRedirect(password_change_url)
    response.set_cookie('back-on-track', request.get_full_path())
    return response


class Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        password_change_url = reverse('password_change')
        if request.user.is_authenticated and request.user.password \
                and request.path != password_change_url:
            if request.user.change_password:
                log.info("request password change, forced, {}".format(request.user))
                return redirect_to_password_change(request, password_change_url)
            if request.user.policy:
                interval = request.user.policy.pass_change_interval
                last_change = request.user.password_changed
                if last_change and interval and (last_change + interval) < now():
                    log.info("request password change, expired, {}".format(request.user))
                    return redirect_to_password_change(request, password_change_url)
        return response
