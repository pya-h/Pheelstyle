
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from decouple import config
from datetime import datetime
from .exceptions import WaitAssholeException
# from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


class MailingInterface:
    template_dir = 'emails/%s.html'
    # EMAIL ONE MINUTE TIME LIMITATION IS FOR ALL USERS
    # MAKE IT USER SPECIFIC
    last_email_date = datetime(1970, 1, 1)
    host = config('EMAIL_HOST_USER')
    SENDGRID_API_KEY = config('SENDGRID_API_KEY')

    @staticmethod
    def SendBySendGrid(target, subject, content):
        message = Mail(
            from_email=MailingInterface.host,
            to_emails=target,
            subject=subject,
            html_content=content)
        try:
            sg = SendGridAPIClient(MailingInterface.SENDGRID_API_KEY)
            response = sg.send(message)
#            print(response.status_code)
#           print(response.body)
#           print(response.headers)
        except Exception as e:
            print(e)

    @staticmethod
    def SendMessage(request, target_email, subject, template_name, dict_content):
        time_passed_from_last_email = datetime.now() - MailingInterface.last_email_date
        if time_passed_from_last_email.total_seconds() > 60:
            domain = get_current_site(request)
            dict_content['user'] = request.user
            dict_content['domain'] = domain
            body = render_to_string(MailingInterface.template_dir % template_name, dict_content)
            # EmailMessage(subject, body, to=[email_address]).send()
            MailingInterface.SendBySendGrid(target_email, subject, body)
        else:
            raise WaitAssholeException(time_passed_from_last_email)

    @staticmethod
    def SendSignedMessage(request, target_email, subject, template_name):
        user = request.user
        time_passed_from_last_email = datetime.now() - MailingInterface.last_email_date
        if time_passed_from_last_email.total_seconds() > 60:
            sender_domain = get_current_site(request)
            body = render_to_string(MailingInterface.template_dir % template_name, {
                'user': user,
                'domain': sender_domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            # EmailMessage(subject, body, to=[email_address]).send()
            MailingInterface.SendBySendGrid(target_email, subject, body)
        else:
            raise WaitAssholeException(time_passed_from_last_email)


    # def __init__(self, user, target_email, request, template):
    #     self.sender_domain = get_current_site(request)
    #     self.user = user
    #     self.template = template
    #     self.default_target = target_email

    # def send(self, subject, new_target=None, new_template=None):
    #     time_passed_from_last_email = datetime.now() - Mailer.last_email_date
    #     if time_passed_from_last_email.total_seconds() > 60:
    #         body = render_to_string(Mailer.template_dir % self.template if not new_template else new_template, {
    #             'user': self.user,
    #             'domain': self.sender_domain,
    #             'uid': urlsafe_base64_encode(force_bytes(self.user.pk)),
    #             'token': default_token_generator.make_token(self.user)
    #         })
    #         # EmailMessage(subject, body, to=[self.default_target if not new_target else new_target]).send()
    #         Mailer.BySendGrid(self.default_target if not new_target else new_target, subject, body)
    #         Mailer.last_email_date = datetime.now()
    #     else:
    #         raise WaitAssholeException(time_passed_from_last_email)
