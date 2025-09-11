import random
import time
from urllib.parse import urlencode

from yunzhanghu_sdk.message import HmacSigner, RSASigner, TripleDes


class Utils(object):
    @staticmethod
    def copy_dict(res: dict):
        res = res.copy()
        del res["_BaseRequest__request_id"]
        return res

    @staticmethod
    def get_customer_link(conf, base_url: str, member_id: str):
        sign_type = conf.sign_type

        __encrypt = None
        if sign_type == "sha256":
            __encrypt = HmacSigner(conf.app_key)
        else:
            __encrypt = RSASigner(conf.app_key, conf.yzh_public_key, conf.dealer_private_key)

        timestamp = int(time.time())
        mess = "".join(random.sample("1234567890abcdefghijklmnopqrstuvwxy", 10))
        data = bytes("member_id={}".format(member_id), encoding="utf8")

        sign = __encrypt.sign(data, mess, timestamp)
        params = {'sign_type': sign_type, "sign": sign, "member_id": member_id, "mess": mess, "timestamp": timestamp}
        return base_url + "?" + urlencode(params)
