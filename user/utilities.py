from .models import User
from django.contrib.auth.backends import BaseBackend


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
