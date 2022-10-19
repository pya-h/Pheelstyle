from django.http import HttpResponse
from django.shortcuts import redirect
import requests
import json
from purchase.models import Order
from django.contrib.auth.decorators import login_required
from purchase.views import finalize_order

merchant_id = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
# amount = 0  # Rial / Required
# email = 'email@example.com'  # Optional
# mobile = '09123456789'  # Optional
# Important: need to edit for real server.


@login_required(login_url='login')
def send_request(request, order_key):
    try:
        callback_url = f'https://{request.get_host()}/zp/verify/{order_key}/'
        order = Order.objects.get(buyer=request.user, is_completed=False, key=order_key)
        if order and order_key:
            amount = order.must_be_paid * 10  # amount of payment in rials
            description = f'Paying {amount} Rials for buying some of the pheelstyle products'  # Required
            req_data = {
                "merchant_id": merchant_id,
                "amount": amount,
                "callback_url": callback_url,
                "description": description,
                "metadata": {"mobile": None, "email": None}
            }
            req_header = {"accept": "application/json",
                          "content-type": "application/json'"}
            req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
                req_data), headers=req_header)
            authority = req.json()['data']['authority']
            if len(req.json()['errors']) == 0:
                return redirect(ZP_API_STARTPAY.format(authority=authority))
            else:
                e_code = req.json()['errors']['code']
                e_message = req.json()['errors']['message']
                return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
        else:
            print('sth went wrong while making the transaction cause: such order can not be found')
            return HttpResponse('such order can not be found')
    except Exception as ex:
        print(f'sth went wrong while making the transaction cause: {ex}')
        return HttpResponse(f"Error: {ex}")


@login_required(login_url='login')
def verify(request, order_key):
    try:
        order = Order.objects.get(buyer=request.user, is_completed=False, key=order_key)
        order.how_much_to_pay()  # calling this is just for making sure that order.must_be_paid is absolutely correct
        if order and order_key:
            amount = order.must_be_paid * 10  # amount of payment in rials

            t_status = request.GET.get('Status')
            t_authority = request.GET['Authority']
            if request.GET.get('Status') == 'OK':
                req_header = {"accept": "application/json",
                              "content-type": "application/json'"}
                req_data = {
                    "merchant_id": merchant_id,
                    "amount": amount,
                    "authority": t_authority
                }
                req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
                if len(req.json()['errors']) == 0:
                    t_status = req.json()['data']['code']
                    if t_status == 100:
                        reference_id = req.json()['data']['ref_id']
                        finalize_order(request=request, order_key=order.key, reference_id=reference_id, \
                                         method='zarinpal', status='successful', amount=amount, was_successful=True)
                        return HttpResponse(f'Transaction success.\nRefID: {reference_id}')
                    elif t_status == 101:
                        return HttpResponse('Transaction submitted : ' + str(req.json()['data']['message']))
                    else:
                        return HttpResponse('Transaction failed.\nStatus: ' + str(req.json()['data']['message']))
                else:
                    e_code = req.json()['errors']['code']
                    e_message = req.json()['errors']['message']
                    return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
            else:
                return HttpResponse('Transaction failed or canceled by user')
        else:
            print('sth went wrong while verifying the transaction cause: such order can not be found')
            return HttpResponse('such order can not be found')
    except Exception as ex:
        print(f'sth went wrong while verifying the transaction by zarinpal cause: {ex}')
        return HttpResponse(f'Error: {ex}')

