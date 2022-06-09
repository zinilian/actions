#!/usr/bin/env python
# -*- coding: utf8 -*-
# 时光相册签到
# https://cloud.tencent.com/developer/article/1617271
import requests
import json
import os

def start(mobile, password):
    header = {
        "User-Agent": "EverPhoto/4.2.0 (Android;2702;ONEPLUS A6000;28;oppo)",
        "x-device-mac": "02:00:00:00:00:00",
        "application":"tc.everphoto",
        "authorization": "Bearer 94P6RfZFfqvVQ2hH4jULaYGI",
        "x-locked":"1",
        "content-length":"0",
        "accept-encoding":"gzip"

    }
    url = "https://api.everphoto.cn/users/self/checkin/v2"
    urllogin = "https://web.everphoto.cn/api/auth"
    loginkey = "mobile=" + mobile + "&password=" + password
    responselogin = requests.post(urllogin,data=loginkey, headers=header)
    logindata = json.loads(responselogin.text)["data"]
    header["authorization"] = "Bearer " + logindata["token"]
    response = requests.post(url, headers=header)
    datas = json.loads(response.text)
    print(datas)

# def main_handler(event, context):
#     start("+8613588285079", "d4e272b48440583ee28042b2a0568ba0")
#     start("+8617816878076", "04d4c4c6fcd6b4c9e7108893e9410d5d")

if __name__ == '__main__':
    env = os.environ
    form_data = env['SGXC_DATA']
    for user_data in form_data.split(';'):
         mobile, password = user_data.split(',')
         print(f'sign in for {mobile} ...')
         start(mobile, password)
         # print(passwd)
         print(f'sign in for {mobile} done') 

