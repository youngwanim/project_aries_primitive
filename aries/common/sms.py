#! /usr/bin/env python2
# encoding:utf-8
# python 2.7 测试通过
# python 3 更换适当的开发库就能使用，在此我们不额外提供

import hashlib
from .tools import SmsSenderUtil


class SmsSingleSender:
    """ 单发类定义"""
    appid = 0
    appkey = ""
    url = "https://yun.tim.qq.com/v5/tlssmssvr/sendsms"

    def __init__(self, appid, appkey):
        self.appid = appid
        self.appkey = appkey
        self.util = SmsSenderUtil()

    def send(self, sms_type, nation_code, phone_number, msg, extend, ext):

        rnd = self.util.get_random()
        cur_time = self.util.get_cur_time()

        sign_str = "appkey=" + self.appkey + "&random=" + str(rnd) \
                   + "&time=" + str(cur_time) + "&mobile=" + phone_number

        data = {}

        tel = {"nationcode": nation_code, "mobile": phone_number}
        data["tel"] = tel
        data["type"] = sms_type
        data["msg"] = msg
        data["sig"] = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
        data["time"] = cur_time
        data["extend"] = extend
        data["ext"] = ext

        whole_url = self.url + "?sdkappid=" + str(self.appid) + "&random=" + str(rnd)
        return self.util.send_post_request("yun.tim.qq.com", whole_url, data)

    def send_with_param(self, nation_code, phone_number, templ_id, params, sign, extend, ext):

        rnd = self.util.get_random()
        cur_time = self.util.get_cur_time()

        data = {}

        tel = {"nationcode": nation_code, "mobile": phone_number}
        data["tel"] = tel
        data["tpl_id"] = templ_id
        data["sign"] = sign
        data["sig"] = self.util.calculate_sig_for_templ(self.appkey, rnd, cur_time, phone_number)
        data["params"] = params
        data["time"] = cur_time
        data["extend"] = extend
        data["ext"] = ext

        whole_url = self.url + "?sdkappid=" + str(self.appid) + "&random=" + str(rnd)
        return self.util.send_post_request("yun.tim.qq.com", whole_url, data)


class SmsMultiSender:
    """ 群发类定义"""
    appid = 0
    appkey = ""
    url = "https://yun.tim.qq.com/v5/tlssmssvr/sendmultisms2"

    def __init__(self, appid, appkey):
        self.appid = appid
        self.appkey = appkey
        self.util = SmsSenderUtil()

    def send(self, sms_type, nation_code, phone_numbers, msg, extend, ext):

        rnd = self.util.get_random()
        cur_time = self.util.get_cur_time()

        data = {}

        data["tel"] = self.util.phone_numbers_to_list(nation_code, phone_numbers)
        data["type"] = sms_type
        data["msg"] = msg
        data["sig"] = self.util.calculate_sig(self.appkey, rnd, cur_time, phone_numbers)
        data["time"] = cur_time
        data["extend"] = extend
        data["ext"] = ext

        whole_url = self.url + "?sdkappid=" + str(self.appid) + "&random=" + str(rnd)
        return self.util.send_post_request("yun.tim.qq.com", whole_url, data)

    def send_with_param(self, nation_code, phone_numbers, templ_id, params, sign, extend, ext):

        rnd = self.util.get_random()
        cur_time = self.util.get_cur_time()

        data = { }

        data["tel"] = self.util.phone_numbers_to_list(nation_code, phone_numbers)
        data["sign"] = sign
        data["sig"] = self.util.calculate_sig_for_templ_phone_numbers(self.appkey, rnd, cur_time, phone_numbers)
        data["tpl_id"] = templ_id
        data["params"] = params
        data["time"] = cur_time
        data["extend"] = extend
        data["ext"] = ext

        whole_url = self.url + "?sdkappid=" + str(self.appid) + "&random=" + str(rnd)
        return self.util.send_post_request("yun.tim.qq.com", whole_url, data)
