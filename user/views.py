from django.shortcuts import render, redirect
from django import forms
from .forms import RegisterForm, InputValidator
from .models import User, Profile
from stack.utlities import attach_current_stack_to_current_user, merge_user_stacks
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .utilities import Mailer
import requests
from common.exceptions import WaitAssholeException


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            fname = form.cleaned_data['fname']
            lname = form.cleaned_data['lname']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(fname=fname, lname=lname, phone=phone, password=password, email=email)
            user.save()
            profile = Profile(user=user)
            profile.save()
            # send user verification email
            Mailer(user, email, request, 'user_verification').send('فعال سازی حساب کاربری')
            # messages.info(request, 'حسابت ساخته شد...حالا از طریقی ایمیلی که برات فرستادیم باید اکانتت رو فعال
            # کنی...')
            return redirect('/user/login/?command=verification&email=' + email)
    else:
        form = RegisterForm()
    context = {
        'form': form
    }
    return render(request, 'user/register.html', context)


def login(request):
    try:
        if request.method == 'POST':
            contact = request.POST['contact']
            password = request.POST['password']
            if contact.isdigit():
                user = auth.authenticate(phone=contact, password=password)
            else:
                user = auth.authenticate(email=contact, password=password)

            if user is None:  # wrong credentials
                messages.error(request, 'متاسفانه آب قطعه!')
                return redirect('login')
            else:  # ok credentials
                attach_current_stack_to_current_user(request=request, user=user)  # must be exactly before auth.login
                auth.login(request, user)
                merge_user_stacks(user)
                messages.success(request, 'دخول شما موفقیت آمیز بود.')
                # get the current ip of the user every time
                user.ip = request.META.get('REMOTE_ADDR')
                user.save()
                # redirect to caller page
                url = request.META.get('HTTP_REFERER')
                query = requests.utils.urlparse(url).query
                if query and query.replace(' ', '') != '':
                    url_params = dict(q.split('=') for q in query.split('&'))
                    # if there is a next parameter in url:
                    if 'next' in url_params and url_params['next'] is not None:
                        return redirect(url_params['next'])
                return redirect('user-dashboard') if not user.is_superuser else redirect('darbar')
    except Exception as ex:
        print('sth went wrong while trying to login: ' + ex.__str__())
    return render(request, 'user/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'خروج با موفقیت انجام شد.')
    return redirect('login')


def activate(request, uidb64, token):
    user = None
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
        # if user returned successfully
        if user is not None and default_token_generator.check_token(user, token):
            user.activated = True
            user.save()
            messages.success(request, 'حساب کاربری شما با موفقیت فعال شد.')
            return redirect('login')
    except(ValueError, TypeError, OverflowError, User.DoesNotExist):
        user = None
    # if sth went wrong
    messages.error(request, 'لینک فعال سازی دیگر معتبر نیست!')
    return redirect('register')


def forgot_password(request):
    try:
        if request.method == 'POST':
            email = request.POST['email']
            if User.objects.filter(email__exact=email).exists():
                user = User.objects.get(email__exact=email)
                if user is None:
                    messages.error(request=request, message='هیچ حساب کاربری با این ایمیل ثبت نشده.')
                else:
                    # send password reset email:
                    Mailer.Send(request=request, user=user, email_address=email, subject='بازیابی رمزشب', template_name='reset_password')
                    messages.info(request=request, message='ایمیل بازیابی رمزشب به آدرس بالا ارسال شد...')
                    return redirect('login')
            else:
                messages.error(request=request, message='هیچ حساب کاربری با این ایمیل ثبت نشده.')
                return redirect('forgot_password')
    except WaitAssholeException as err:
        messages.error(request=request, message=err.fa())
    except Exception as ex:
        print(ex)
        messages.error(request=request, message='مشکلی حین ارسال ایمیل پیش آمد...ایمیل رو درست وارد کردی؟')
    return render(request, 'user/forgot_password_form.html')


def reset_password_permission(request, uidb64, token):
    user = None
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
        # if user returned successfully
        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid'] = uid
            messages.success(request, 'حالا می تونی یه رمزشب نو واسه ی خودت انتخاب کنی.')
            return redirect('reset_password')
    except(ValueError, TypeError, OverflowError, User.DoesNotExist):
        user = None
    # if sth went wrong
    messages.error(request, 'لینک بازیابی رمزشب دیگر معتبر نیست!')
    return redirect('forgot_password')


def reset_password(request):
    if request.method == 'POST':
        try:
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']

            if password == confirm_password:
                # now change the password
                InputValidator.password_check(password=password)
                uid = request.session.get('uid')
                user = User.objects.get(pk=uid)
                if user is not None:
                    user.set_password(password)
                    user.save()
                    messages.success(request=request, message='رمزشب شما با موفقیت تغییر داده شد!')
                    return redirect('login')
                else:
                    messages.warning(request=request, message='حساب کاربری یافت نشد... لطفا دوباره تلاش کن!')
                    return redirect('login')
            else:
                messages.warning(request=request, message='رمزشب باید با تکرارش مطابقت کامل داشته باشد!')
                return redirect('reset_password')
        except forms.ValidationError as ex:
            messages.warning(request=request, message=ex.message)
            return redirect('reset_password')
        except:
            messages.warning(request=request, message='خطای نامشخصی رخ داده است... لطفا از نو تلاش کنید!')
            return redirect('reset_password')
    return render(request, 'user/reset_password_form.html')
