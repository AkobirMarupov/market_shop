import random
import requests


def send_eskiz_sms(phone):
    code = "".join([str(random.randint(0, 9)) for _ in range(4)])

    url = "http://notify.eskiz.uz/api/auth/login"

    payload = {'email': 'imronhoja336@mail.ru',
               'password': 'ombeUIUC8szPawGi3TXgCjDXDD0uAIx2AmwLlX9M'}

    files = [

    ]
    headers = {
        # 'Authorization': f"{Bearer}"
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    token1 = response.json()["data"]["token"]

    url = "http://notify.eskiz.uz/api/message/sms/send"

    payload = {'mobile_phone': str(phone),
               'message': f"Envoy ilovasiga ro‘yxatdan o‘tish uchun tasdiqlash kodi: {code}",
               'from': '4546',
               'callback_url': 'http://0000.uz/test.php'}
    files = [

    ]

    headers = {
        'Authorization': f"Bearer {token1}"
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    return code
