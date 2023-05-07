from .models import User
from django.contrib.auth.backends import BaseBackend
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from datetime import datetime
from common.exceptions import WaitAssholeException


# custom authenticate class and method
class UserLoginBackend(BaseBackend):
    def authenticate(self, request, phone=None, email=None, password=None):
        print(request, phone, email, password)
        try:
            user = None

            if phone is not None:  # for loging in from django admin  anel
                user = User.objects.get(phone=phone)
            elif email is not None:  # normal custom log in
                user = User.objects.get(email__exact=email)

            if user is not None and user.check_password(password):
                return user

        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


# -----------------------------------------------------------------------------------------------

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from decouple import config

# EMAIL ONE MINUTE TIME LIMITATION IS FOR ALL USERS
# MAKE IT USER SPECIFIC


class Mailer:
    # email send helper
    template_dir = 'emails/%s.html'
    last_email_date = datetime(1970, 1, 1)
    host = config('EMAIL_HOST_USER')
    SENDGRID_API_KEY = config('SENDGRID_API_KEY')

    def __init__(self, user, target_email, request, template):
        self.sender_domain = get_current_site(request)
        self.user = user
        self.template = template
        self.default_target = target_email

    def send(self, subject, new_target=None, new_template=None):
        time_passed_from_last_email = datetime.now() - Mailer.last_email_date
        if time_passed_from_last_email.total_seconds() > 60:
            body = render_to_string(Mailer.template_dir % self.template if not new_template else new_template, {
                'user': self.user,
                'domain': self.sender_domain,
                'uid': urlsafe_base64_encode(force_bytes(self.user.pk)),
                'token': default_token_generator.make_token(self.user)
            })
            # EmailMessage(subject, body, to=[self.default_target if not new_target else new_target]).send()
            Mailer.BySendGrid(self.default_target if not new_target else new_target, subject, body)
            Mailer.last_email_date = datetime.now()
        else:
            raise WaitAssholeException(time_passed_from_last_email)

    @staticmethod
    def BySendGrid(target, subject, content):
        message = Mail(
            from_email=Mailer.host,
            to_emails=target,
            subject=subject,
            html_content=content)
        try:
            sg = SendGridAPIClient(Mailer.SENDGRID_API_KEY)
            response = sg.send(message)
#            print(response.status_code)
#           print(response.body)
#           print(response.headers)
        except Exception as e:
            print(e)

    @staticmethod
    def Send(request, user, email_address, subject, template_name):
        time_passed_from_last_email = datetime.now() - Mailer.last_email_date
        if time_passed_from_last_email.total_seconds() > 60:
            sender_domain = get_current_site(request)
            body = render_to_string(Mailer.template_dir % template_name, {
                'user': user,
                'domain': sender_domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            # EmailMessage(subject, body, to=[email_address]).send()
            Mailer.BySendGrid(email_address, subject, body)
        else:
            raise WaitAssholeException(time_passed_from_last_email)