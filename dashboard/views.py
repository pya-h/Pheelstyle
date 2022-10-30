from django.contrib.auth.decorators import login_required
from purchase.models import Order, OrderedProduct
from django.shortcuts import render, get_object_or_404, redirect
from user.models import Profile, User
from .forms import UserEditForm, ProfileEditForm
from django.contrib import messages


@login_required(login_url='login')
def user_dashboard(request):
    context = {}
    try:
        context['your_orders_count'] = Order.objects.filter(buyer=request.user, status='certified').count()
    except:
        context['your_orders_count'] = 'خطای بارگذاری'
    return render(request, 'dashboard/index.html', context)


@login_required(login_url='login')
def user_orders(request):
    status = {'new': 'جدید',
              'pending': 'در دست بررسی',
              'certified': 'سفارش معتبر',
              'sent': ' ارسال شده',
              'delivered': 'تحویل شده',
              'uncertified': 'سفارش نامعتبر',
              'not_sent': 'عدم ارسال',
              'undelivered': 'عدم تحویل',
              'canceled': 'داستان',
              'failed': 'قطعی آب'
              }
    context = {}
    try:
        context['your_orders'] = Order.objects.filter(buyer=request.user).order_by('-date_created')
        for order in context['your_orders']:
            order.status_fa = status[str(order.status)]
    except:
        context['your_orders'] = 'خطای بارگذاری'

    return render(request, 'dashboard/your_orders.html', context)


@login_required(login_url='login')
def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = get_object_or_404(Profile, user=request.user)
    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'پروفایلت آپدیت شد.')
            return redirect('user-profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=user_profile)

    return render(request, 'dashboard/profile.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required(login_url='login')
def change_pass(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        try:

            password = request.POST["password"]
            new_pass = request.POST["new-pass"]
            confirm_pass = request.POST["confirm-pass"]

            if new_pass != confirm_pass:
                messages.error(request, "رمز شب جدیدت با تاییدیه ش مطابقت نداره که!")
                return redirect('user-chpwd')

            user = User.objects.get(id__exact=request.user.id)
            if not user:
                messages.error(request, 'کاربر کنونی غیر معتبر تشریف دارد!')
                return redirect('login')

            # now check  that old password is correct
            if not user.check_password(password):
                messages.error(request, "در صورتی که رمز شبت رو اشتباه بزنی امکان تغییر رمز وجود نداره! ")
                return redirect('user-chpwd')

            # if everything checks out, then try to change th pas:
            user.set_password(new_pass)
            user.save()
            messages.info(request, "رمز شب شما تغییر یافت.")
            return redirect('logout')

        except User.DoesNotExist:
            messages.error(request, 'کاربر کنونی غیر معتبر تشریف دارد!')
            return redirect('login')
        except:
            pass
    return render(request, 'dashboard/change_pass.html')


@login_required(login_url='login')
def view_order(request, order_key):
    if not request.user.is_authenticated:
        return redirect('login')
    context = {}
    try:
        context['order'] = Order.objects.get(key=order_key)
        context['its_products'] = OrderedProduct.objects.filter(order__key=order_key)
    except Order.DoesNotExist or OrderedProduct.DoesNotExist:
        messages.error(request, "همچین زد و بندی نداشتیم ما با هم!")
        return redirect('user-orders')

    return render(request, 'dashboard/single_order.html', context)