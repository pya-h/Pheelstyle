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
        new_user.is_staff = new_user.is_superuser = False
        new_user.save(using=self._db)
        return new_user

    def create_superuser(self, phone, password, fname, lname, email):
        self.validate_credentials(phone, password, fname, lname, email)
        owner = self.model(phone=phone, fname=fname, lname=lname, email=self.normalize_email(email))
        owner.set_password(password)
        owner.is_activated = False
        owner.is_staff = owner.is_superuser = True
        owner.save(using=self._db)
        return owner


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fname = models.CharField(max_length=30, verbose_name="اسم")
    lname = models.CharField(max_length=30, verbose_name="فامیل")
    # login field is phone number or email
    phone = models.CharField(max_length=11, unique=True, verbose_name="تیلیف")
    email = models.CharField(max_length=100, unique=True, verbose_name="نومه")
    ip = models.CharField(max_length=20, blank=True, verbose_name="IP")
    last_email_date = models.DateTimeField(default=None, blank=True, null=True)
    # age, whatever, etc..

    # requirements:
    joining_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ فیلی شدن")
    last_login = models.DateTimeField(auto_now=True, verbose_name="آخرین دخول")
    is_staff = models.BooleanField(default=False, verbose_name="فیل درباری")
    is_superuser = models.BooleanField(default=False, verbose_name="فیل شاه")
    is_activated = models.BooleanField(default=False, verbose_name="فعال شدن اکانت")
    # is active, is online , ... ?

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['fname', 'lname', 'email']
    objects = UserManager()

    def __str__(self) -> str:
        return f'{self.fname} {self.lname}'

    def ID(self):
        return self.id

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, add_label):
        return self.is_superuser

    class Meta:
        verbose_name = "فیلی"
        verbose_name_plural = "فیلی ها"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="کاربر")
    postal_code = models.CharField(max_length=10, verbose_name="کدپستی", blank=True)
    province = models.CharField(max_length=30, verbose_name="استان", blank=True)
    city = models.CharField(max_length=30, verbose_name="شهرستان", blank=True)
    address = models.TextField(max_length=256, verbose_name="نشونی", blank=True)
    avatar = models.ImageField(blank=True, upload_to='photos/avatars/', null=True)

    debt = models.IntegerField(default=0, verbose_name='بدهی شما')

    def full_address(self):
        return f'{self.province} - {self.city} - {self.address}'

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل ها"
