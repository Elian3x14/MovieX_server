# payments.py

import time
import hmac
import hashlib
import json
import requests
from django.conf import settings


def create_zalopay_payment(booking_id: int, amount: int):
    """
    Gửi yêu cầu tạo đơn thanh toán tới ZaloPay Sandbox.

    Args:
        booking_id (int): ID của đơn đặt chỗ (Booking).
        amount (int): Số tiền thanh toán (VND). Mặc định là 1.000.

    Returns:
        dict: Kết quả response từ ZaloPay.
    """
    app_id = settings.ZALOPAY_APP_ID
    key1 = settings.ZALOPAY_KEY1

    app_trans_id = time.strftime("%y%m%d") + "_" + str(int(time.time()))
    app_user = f"user_{booking_id}"
    app_time = int(time.time() * 1000)

    embed_data = json.dumps({})
    items = json.dumps([])

    data_string = f"{app_id}|{app_trans_id}|{app_user}|{amount}|{app_time}|{embed_data}|{items}"
    mac = hmac.new(key1.encode(), data_string.encode(), hashlib.sha256).hexdigest()

    order_payload = {
        "app_id": app_id,
        "app_user": app_user,
        "app_time": app_time,
        "amount": amount,
        "app_trans_id": app_trans_id,
        "bank_code": "zalopayapp",
        "embed_data": embed_data,
        "item": items,
        "callback_url": settings.ZALOPAY_CALLBACK_URL,
        "description": f"Thanh toán đơn hàng #{booking_id}",
        "mac": mac
    }

    response = requests.post(settings.ZALOPAY_SANDBOX_ENDPOINT, data=order_payload)
    return response.json()
