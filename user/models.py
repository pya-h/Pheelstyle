import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def validate_credentials(self, phone, password, fname, lname, email):
        if not phone:
            raise ValueError('Phone number field is essential')
        if not password: # and some other properties
            raise ValueError('Password must be stronger')
        if not fname or not lname:
            raise ValueError('Both name fields are essential')
        
    def create_user(self, phone, password, fname, lname, email):
        self.validate_credentials(phone, password, fname, lname, email)
        new_user = self.model(phone=phone, fname=fname, lname=lname, email=self.normalize_email(email))
        new_user.set_password(password)
        new_user.is_admin = new_user.is_staff = False
        new_user.is_superuser = False
        new_user.save(using=self._db)
        return new_user
    
    def create_superuser(self, phone, password, fname, lname, email):
        self.validate_credentials(phone, password, fname, lname, email)
        owner = self.model(phone=phone, fname=fname, lname=lname, email=self.normalize_email(email))
        owner.set_password(password)
        owner.activated = False
        owner.is_staff = owner.is_admin = owner.is_superuser = True
        owner.save(using=self._db)
        return owner


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fname = models.CharField(max_length=30, verbose_name="First Name")
    lname = models.CharField(max_length=30, verbose_name="Last Name")
    # login field is phone number or email
    phone = models.CharField(max_length=11, unique=True, verbose_name="Phone Number")
    email = models.CharField(max_length=100, unique=True, verbose_name="E-mail")
    ip = models.CharField(max_length=20, blank=True, verbose_name="IP")
    # age, whatever, etc..

    # requirements:
    joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    activated = models.BooleanField(default=False)
    # is active, is online , ... ?

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['fname', 'lname', 'email']
    objects = UserManager()

    def __str__(self) -> str:
        return f'{self.fname} {self.lname}'

    def ID(self):
        return self.id

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

