#!/usr/bin/env python
# coding=utf-8
# 天翼云盘签到/抽奖
import os
import base64
import re
import time

import requests
import rsa

TITLE = '天翼云盘'


def _chr(a):
    return "0123456789abcdefghijklmnopqrstuvwxyz"[a]


b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def b64_to_hex(a):
    d = ""
    e = 0
    c = 0
    for i in range(len(a)):
        if list(a)[i] != "=":
            v = b64map.index(list(a)[i])
            if 0 == e:
                e = 1
                d += _chr(v >> 2)
                c = 3 & v
            elif 1 == e:
                e = 2
                d += _chr(c << 2 | v >> 4)
                c = 15 & v
            elif 2 == e:
                e = 3
                d += _chr(c)
                d += _chr(v >> 2)
                c = 3 & v
            else:
                e = 0
                d += _chr(c << 2 | v >> 4)
                d += _chr(15 & v)
    if e == 1:
        d += _chr(c << 2)
    return d


class Clound189(object):
    LOGIN_URL = "https://cloud.189.cn/api/portal/loginUrl.action?" \
                "redirectURL=https://cloud.189.cn/web/redirect.html?returnURL=/main.action"
    SUBMIT_LOGIN_URL = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
    SIGN_URL = ("https://api.cloud.189.cn/mkt/userSign.action?rand=%s"
                "&clientType=TELEANDROID&version=8.6.3&model=SM-G930K")

    def __init__(self, username, password):
        self._client = requests.Session()
        self._username = username
        self._password = password

    def checkin(self):
        self.login()
        msg = {}
        result = {
            'code': 0,
            'msg': msg
        }
        rand = str(round(time.time() * 1000))
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv)"
                          " AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74"
                          ".0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clie"
                          "ntId/355325117317828 clientModel/SM-G930K imsi/46007111431782"
                          "4 clientChannelId/qq proVersion/1.0.6",
            "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
            "Host": "m.cloud.189.cn",
            "Accept-Encoding": "gzip, deflate",
        }
        response = self._client.get(self.SIGN_URL % rand, headers=headers)
        net_disk_bonus = response.json()["netdiskBonus"]
        if response.json()["isSign"] == "false":
            result['code'] = 0
            print("签到成功")
        else:
            result['code'] = 1
            print("今日已签到")
        msg['checkin'] = f"签到获得{net_disk_bonus}M空间"
        print(msg['checkin'])

        # 抽奖
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0"
                          ".3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientI"
                          "d/355325117317828 clientModel/SM-G930K imsi/460071114317824 cl"
                          "ientChannelId/qq proVersion/1.0.6",
            "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
            "Host": "m.cloud.189.cn",
            "Accept-Encoding": "gzip, deflate",
        }
        url1 = "https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN"
        url2 = "https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN"
        msg['prize_name'] = []
        for i, url in enumerate((url1, url2)):
            response = self._client.get(url, headers=headers)
            if "errorCode" in response.text:
                errcode = response.json().get('errorCode')
                print(f"没有抽奖机会: {errcode}")
            else:
                prize_name = (response.json() or {}).get("prizeName")
                message = f"抽奖获得{prize_name}"
                msg['prize_name'].append(message)
                print(message)
        return result

    @staticmethod
    def rsa_encode(rsa_key, string):
        rsa_key = f"-----BEGIN PUBLIC KEY-----\n{rsa_key}\n-----END PUBLIC KEY-----"
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
        result = b64_to_hex(
            (base64.b64encode(rsa.encrypt(f"{string}".encode(), pubkey))).decode())
        return result

    def login(self):
        r = self._client.get(self.LOGIN_URL)
        captcha_token = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
        lt = re.findall(r'lt = "(.+?)"', r.text)[0]
        return_url = re.findall(r"returnUrl = '(.+?)'", r.text)[0]
        param_id = re.findall(r'paramId = "(.+?)"', r.text)[0]
        j_rsa_key = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
        self._client.headers.update({"lt": lt})
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0",
            "Referer": "https://open.e.189.cn/",
        }
        data = {
            "appKey": "cloud",
            "accountType": "01",
            "userName": f"{{RSA}}{self.rsa_encode(j_rsa_key, self._username)}",
            "password": f"{{RSA}}{self.rsa_encode(j_rsa_key, self._password)}",
            "validateCode": "",
            "captchaToken": captcha_token,
            "returnUrl": return_url,
            "mailSuffix": "@189.cn",
            "paramId": param_id,
        }
        r = self._client.post(self.SUBMIT_LOGIN_URL,
                              data=data, headers=headers, timeout=5)
        if r.json()["result"] == 0:
            print(r.json()["msg"])
        else:
            print(r.json()["msg"])
        redirect_url = r.json()["toUrl"]
        self._client.get(redirect_url)

    @staticmethod
    def start(push=None):
        data = os.environ['CLOUD189_ACCOUNTS']
        for user_data in data.split(';'):
            username, password = user_data.split(',')
            try:
                account = Clound189(username, password)
                res = account.checkin()
                push and push(TITLE, Clound189.getmsg(username, res))
            except Exception as e:
                push and push(TITLE, str(e))

    @staticmethod
    def getmsg(username, result):
        code = result.get('code')
        msg = result['msg']
        if code >= 0:
            if code == 0:
                ret = "签到成功"
            elif code == 1:
                ret = "今日已签到"
            ret += f"({username})\n{msg['checkin']}"
            for prize_name in msg['prize_name']:
                ret += f"\n{prize_name}"
        else:
            # 签到失败
            ret = "签到失败"
        return ret


if __name__ == "__main__":
    Clound189.start()
