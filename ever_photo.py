#!/usr/bin/env python
# coding=utf-8
# 时光相册签到
import requests
import hashlib
import os


class EverPhoto(object):
    NAME = "时光相册"
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
        data = {
            "mobile": f"+86{self._mobile}",
            "password": self.salt(self._password),
        }
        res = requests.post(self.LOGIN_URL, data=data,
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

        msg = []
        res = requests.post(self.CHECKIN_URL, headers=headers).json()
        if res.get("code") == 0:
            data = res.get("data")
            if data.get("checkin_result"):
                print(f"✔️ checkin success: {self._mobile}")
                msg.append("签到成功")
                msg.append({
                    "name": "奖励空间",
                    "value": f"{data['reward'] / (1024 * 1024)}MB",
                })
                msg.append({
                    "name": "已连续签到",
                    "value": f"{data['continuity']}天",
                })
                msg.append({
                    "name": "已获奖励",
                    "value": f"{data['total_reward'] / (1024 * 1024)}MB",
                })
                msg.append({
                    "name": "明日可领",
                    "value": f"{data['tomorrow_reward'] / (1024 * 1024)}MB",
                })
                print(msg)
            else:
                print(f"✔️ checkin already: {self._mobile}")
                msg.append("今日已签到")
        else:
            print(f"❌ checkin error: {res.get('message')}")
            raise Exception(f"签到失败: {res.get('message')}")
        return msg

    @staticmethod
    def start():
        msg = []
        data = os.environ['EVER_PHOTO_ACCOUNTS']
        for user_data in data.split(';'):
            mobile, password = user_data.split(',')
            msg.append(f"---账号: {mobile}---")
            account = EverPhoto(mobile, password)
            res = account.checkin()
            msg.append(res)
        return msg


if __name__ == '__main__':
    EverPhoto.start()
