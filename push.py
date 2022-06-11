#!/usr/bin/env python
# coding=utf-8

import requests
import os


class WeWorkPush(object):
    """企业微信应用消息推送"""

    URL_BASE = "https://qyapi.weixin.qq.com/cgi-bin/"
    URL_TOKEN = "gettoken"
    URL_SEND = "message/send?access_token={}"

    def __init__(self, config=None):
        self.config = {}
        self.token = None
        self.setup(config)
        self.get_token()

    def setup(self, config=None):
        if config is None:
            # setup from env
            self.config['corp_id'] = os.environ['WX_CORP_ID']
            self.config['app_id'] = int(os.environ['WX_APP_ID'])
            self.config['app_secret'] = os.environ['WX_APP_SECRET']
        else:
            self.config['corp_id'] = config['corp_id']
            self.config['app_id'] = config['app_id']
            self.config['app_secret'] = config['app_secret']

    def get_token(self):
        params = {
            "corpid": self.config['corp_id'],
            "corpsecret": self.config['app_secret'],
        }
        res = requests.get(self.URL_BASE + self.URL_TOKEN, params=params)
        res.raise_for_status()
        res = res.json()
        self.token = res.get('access_token')
        return self.token

    def send(self, content="", url=None):
        res = self._send(content, url)
        if res.get('errcode') != 0:
            # expired token?
            self.get_token()
            res = self._send(content, url)
            if res.get('errcode') != 0:
                raise Exception(res.get('errmsg'))
        print(f"✔️ send message: {content}")

    def _send(self, content, url):
        url_send = (self.URL_BASE + self.URL_SEND).format(self.token)
        content = f'{content}\n'
        if url is not None:
            content += f'\n<a href="{url}">查看详情</a>'
        message = {
            "touser": "@all",
            "msgtype": "text",
            "agentid": self.config['app_id'],
            "text": {
                "content": content
            }
        }
        res = requests.post(url_send, json=message)
        res.raise_for_status()
        return res.json()


if __name__ == "__main__":
    config = {
        'corp_id': "",
        'app_secret': "",
        'app_id': 1,
    }
    pusher = WeWorkPush(config)
    pusher.send('hello world!\nHello Again!',
                url="https://github.com/ZenLian/actions/actions")
