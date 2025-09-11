from django.contrib.auth import logout
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now

"""
requires the user model to have the field
`force_logout_date = models.DateTimeField(null=True, blank=True, default=None)`
then add to the project middleware after `AuthenticationMiddleware`


Move to account service

"""


class Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.session:
            if request.user.force_logout_date:
                if 'LAST_LOGIN_DATE' not in request.session:
                    logout(request)
                elif request.session['LAST_LOGIN_DATE'] < request.user.force_logout_date.isoformat():
                    logout(request)
        return self.get_response(request)


def update_session_last_login(sender, user=None, request=None, **kwargs):
    if request:
        login_date = now()
        request.session['LAST_LOGIN_DATE'] = login_date.isoformat()


user_logged_in.connect(update_session_last_login)
