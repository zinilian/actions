#!/usr/bin/env python
# coding=utf-8
# microsoft e5 续订
# references:
# - https://gitee.com/ICE99125/AutoAPI
# - https://github.com/arcturus-script/E5
# - https://github.com/jing5460/AutoApi-E5
import random
# import time
import requests
import os

fixed_api = [
    r'https://graph.microsoft.com/v1.0/me/',
    r'https://graph.microsoft.com/v1.0/users',
    r'https://graph.microsoft.com/v1.0/me/drive/root',
    r'https://graph.microsoft.com/v1.0/me/drive/root/children',
    r'https://graph.microsoft.com/v1.0/me/messages',
    r'https://graph.microsoft.com/v1.0/me/mailFolders',
]

extra_api = [
    # r'https://graph.microsoft.com/v1.0/me/',
    # r'https://graph.microsoft.com/v1.0/users',
    r'https://graph.microsoft.com/v1.0/me/people',
    r'https://graph.microsoft.com/v1.0/groups',
    r'https://graph.microsoft.com/v1.0/me/contacts',
    # r'https://graph.microsoft.com/v1.0/me/drive/root',
    # r'https://graph.microsoft.com/v1.0/me/drive/root/children',
    r'https://graph.microsoft.com/v1.0/drive/root',
    r'https://graph.microsoft.com/v1.0/me/drive',
    r'https://graph.microsoft.com/v1.0/me/drive/recent',
    r'https://graph.microsoft.com/v1.0/me/drive/sharedwithme',
    r'https://graph.microsoft.com/v1.0/me/calendars',
    r'https://graph.microsoft.com/v1.0/me/events',
    r'https://graph.microsoft.com/v1.0/sites/root',
    r'https://graph.microsoft.com/v1.0/sites/root/sites',
    r'https://graph.microsoft.com/v1.0/sites/root/drives',
    r'https://graph.microsoft.com/v1.0/sites/root/columns',
    r'https://graph.microsoft.com/v1.0/me/onenote/notebooks',
    r'https://graph.microsoft.com/v1.0/me/onenote/sections',
    r'https://graph.microsoft.com/v1.0/me/onenote/pages',
    # r'https://graph.microsoft.com/v1.0/me/messages',
    # r'https://graph.microsoft.com/v1.0/me/mailfolders',
    r'https://graph.microsoft.com/v1.0/me/outlook/mastercategories',
    r'https://graph.microsoft.com/v1.0/me/mailfolders/inbox/messages/delta',
    r'https://graph.microsoft.com/v1.0/me/mailfolders/inbox/messagerules',
    r"https://graph.microsoft.com/v1.0/me/messages?$filter=importance eq 'high'",
    r'https://graph.microsoft.com/v1.0/me/messages?$search="hello world"',
    r'https://graph.microsoft.com/beta/me/messages?$select=internetmessageheaders&$top',
]


class MSE5(object):
    NAME = "MicroSoftE5 续订"

    def __init__(self, refresh_token, client_id, client_secret):
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.gettoken()
        # random api list order
        self.api_list = fixed_api.copy()
        extra_list = random.sample(extra_api, 6)
        self.api_list.extend(extra_list)
        random.shuffle(self.api_list)

    def runapi(self):
        # localtime = time.asctime(time.localtime(time.time()))
        headers = {
            'Authorization': self.access_token,
            'Content-Type': 'application/json'
        }
        count = 0
        for api in self.api_list:
            try:
                if requests.get(api, headers=headers).status_code == requests.codes.OK:
                    count += 1
                    print(f"api call success({api})")
            except Exception as e:
                print(f"api call fail({api}): {str(e)}")
        return count, len(self.api_list)

    def gettoken(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': 'http://localhost:53682/'
        }
        res = requests.post(
            'https://login.microsoftonline.com/common/oauth2/v2.0/token', data=data, headers=headers).json()
        if 'refresh_token' not in res:
            print(r'[ERROR] mse5: get token failed')
            return
        # refresh_token = res['refresh_token']
        # print('refresh_token: ' + refresh_token)
        access_token = res['access_token']
        return access_token

    @staticmethod
    def start():
        msg = []
        app_num = os.getenv('MS_APP_NUM', '1')
        clients = []

        print(f'MSE5: {app_num} clients total')
        for i in range(1, int(app_num) + 1):
            if i == 1:
                refresh_token = os.getenv(
                    'MS_TOKEN') or os.getenv('MS_TOKEN_1')
                client_id = os.getenv(
                    'MS_CLIENT_ID') or os.getenv('MS_CLIENT_ID_1')
                client_secret = os.getenv(
                    'MS_CLIENT_SECRET') or os.getenv('MS_CLIENT_SECRET_1')
            else:
                refresh_token = os.getenv(f'MS_TOKEN_{i}')
                client_id = os.getenv(f'MS_CLIENT_ID_{i}')
                client_secret = os.getenv(f'MS_CLIENT_SECRET_{i}')
            client = MSE5(refresh_token, client_id, client_secret)
            clients.append(client)

        for i, client in enumerate(clients):
            msg.append(f'-- 客户端 {i+1}/{len(clients)} --')
            if not client.access_token:
                print(
                    f'[ERROR] MSE5: cannot get access token for client#{i+1}'
                )
                msg.append('无法获取 access token')
                continue
            N = 3
            success_apis, total_apis = 0, 0
            for n in range(N):
                print(
                    f'[INFO] MSE5: running api for client#{i+1}, {n+1}/{N} ...'
                )
                success_api_count, total_api_count = client.runapi()
                success_apis += success_api_count
                total_apis += total_api_count
            msg.append(f'成功调用 api: {success_apis}/{total_apis}')

        return msg


if __name__ == "__main__":
    from main import push_msg
    msg_list = []
    msg_list.append(f"「{MSE5.NAME}」")
    try:
        msg_list.append(MSE5.start())
    except Exception as e:
        msg_list.append(f'{e}')
    push_msg(msg_list)
