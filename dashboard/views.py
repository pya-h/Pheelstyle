from django.contrib.auth.decorators import login_required
from purchase.models import Order
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