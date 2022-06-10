#!/usr/bin/env python
# -*- coding: utf8 -*-
# 时光相册签到
import requests
import hashlib
import os


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
        self.login()

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
                print(f"reward: {data['reward'] / (1024 * 1024)}")
                print(f"continuity: {data['continuity']}")
                print(f"total_reward: {data['total_reward'] / (1024 * 1024)}")
                print(
                    f"tomorrow_reward: {data['tomorrow_reward'] / (1024 * 1024)}")
                # print(f"data: {data}")
            else:
                print(f"✔️ checkin already: {self._mobile}")
        else:
            print(f"❌ checkin error: {res.get('message')}")


if __name__ == '__main__':
    env = os.environ
    form_data = env['EVER_PHOTO_DATA']
    for user_data in form_data.split(';'):
        mobile, password = user_data.split(',')
        account = EverPhoto(mobile, password)
        account.checkin()
