from django.contrib.auth.decorators import login_required
from purchase.models import Order
from django.shortcuts import render


@login_required(login_url='login')
def user_dashboard(request):
    context = {}
    try:
        context['your_orders_count'] = Order.objects.filter(buyer=request.user, status='certified').count()
    except:
        context['your_orders_count'] = 'خطای بارگذاری'
    return render(request, 'dashboard/index.html', context)


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
