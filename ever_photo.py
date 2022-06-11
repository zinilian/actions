#!/usr/bin/env python
# coding=utf-8
# 时光相册签到
import requests
import hashlib
import os

TITLE = "时光相册"


class EverPhoto(object):
    LOGIN_URL = "https://web.everphoto.cn/api/auth"
    CHECKIN_URL = "https://openapi.everphoto.cn/sf/3/v4/PostCheckIn"
    SALT = "tc.everphoto."

    def __init__(self, mobile, password):
        self._mobile = mobile
        self._password = password
        self._headers = {
            "user-agent": "EverPhoto/4.5.0 (Android;2702;ONEPLUS A6000;28;oppo)",
            "application": "tc.everphoto",
        }

    def salt(self, value):
        return hashlib.md5((self.SALT + value).encode()).hexdigest()

    def login(self):
        form = {
            "mobile": f"+86{self._mobile}",
            "password": self.salt(self._password),
        }
        # form = f"mobile={self._mobile}&password={self._password}"
        res = requests.post(self.LOGIN_URL, data=form,
                            headers=self._headers).json()
        if res.get("code") == 0:
            print(f"✔️ login success: {self._mobile}")
            data = res.get("data")
            # print(f"data: {data}")
            self._headers.update({"authorization": f"Bearer {data['token']}"})
        else:
            msg = res.get("message")
            print(f"❌ login error: {msg}")
            raise Exception(msg)

    def checkin(self):
        self.login()

        headers = {
            "content-type": "application/json",
            "host": "openapi.everphoto.cn",
            "connection": "Keep-Alive",
        }

        headers.update(self._headers)

        res = requests.post(self.CHECKIN_URL, headers=headers).json()
        if res.get("code") == 0:
            data = res.get("data")
            if data.get("checkin_result"):
                print(f"✔️ checkin success: {self._mobile}")
                msg = {
                    "reward": data['reward'] / (1024 * 1024),
                    "continuity": data['continuity'],
                    "total_reward": data['total_reward'] / (1024 * 1024),
                    "tomorrow_reward": data['tomorrow_reward'] / (1024 * 1024),
                }
                print(msg)
                return {
                    "code": 0,
                    "msg": msg
                }
            else:
                print(f"✔️ checkin already: {self._mobile}")
                return {
                    "code": 1,
                    "msg": "已签到"
                }
        else:
            print(f"❌ checkin error: {res.get('message')}")
            return {
                "code": -1,
                "msg": res.get('message')
            }

    @staticmethod
    def start(push):
        form_data = os.environ['EVER_PHOTO_DATA']
        for user_data in form_data.split(';'):
            mobile, password = user_data.split(',')
            try:
                account = EverPhoto(mobile, password)
                res = account.checkin()
                push(TITLE, EverPhoto.getmsg(mobile, res))
            except Exception as e:
                push(TITLE, str(e))

    @staticmethod
    def getmsg(mobile, result):
        code = result.get('code')
        if code == 0:
            msg = result['msg']
            return f"签到成功({mobile})\n" +\
                f"奖励空间: {msg['reward']}MB\n" +\
                f"已连续签到: {msg['continuity']}天\n" +\
                f"已获奖励: {msg['total_reward']}MB\n" +\
                f"明日可领: {msg['tomorrow_reward']}MB"
        elif code == 1:
            return f"今日已签到({mobile})"
        else:
            return f"签到失败({mobile})\n" + result.get('msg')


if __name__ == '__main__':
    EverPhoto.start()
