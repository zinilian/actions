#!/usr/bin/env python
# coding=utf-8
# 有道云笔记
import os

import requests


class YouDao(object):
    NAME = "有道云笔记"
    REFRESH_COOKIES_URL = "http://note.youdao.com/login/acc/pe/getsess?product=YNOTE"

    def __init__(self, cookies):
        self._cookies = {item.split("=")[0]: item.split(
            "=")[1] for item in cookies.split("; ")}
        try:
            ynote_pers = self._cookies.get("YNOTE_PERS", "")
            uid = ynote_pers.split("||")[-2]
        except Exception as e:
            print(f"获取账号信息失败: {e}")
            uid = "Unknown"
        self.uid = uid
        pass

    def checkin(self):
        ad_space = 0
        refresh_cookies_res = requests.get(
            self.REFRESH_COOKIES_URL, cookies=self._cookies)
        cookies = dict(refresh_cookies_res.cookies)
        url = "https://note.youdao.com/yws/api/daupromotion?method=sync"
        res = requests.post(url=url, cookies=cookies)
        if "error" not in res.text:
            checkin_response = requests.post(
                url="https://note.youdao.com/yws/mapi/user?method=checkin", cookies=cookies
            )
            for i in range(3):
                ad_response = requests.post(
                    url="https://note.youdao.com/yws/mapi/user?method=adRandomPrompt", cookies=cookies
                )
                ad_space += ad_response.json().get("space", 0) // 1048576
            if "reward" in res.text:
                sync_space = res.json().get("rewardSpace", 0) // 1048576
                checkin_space = checkin_response.json().get("space", 0) // 1048576
                space = sync_space + checkin_space + ad_space
                msg = {
                    "name": "签到成功",
                    "value": f"+{space}M",
                }
            else:
                msg = "获取失败"
        else:
            raise Exception(f"签到失败: {res.json().get('error')}")
        return msg

    @staticmethod
    def start():
        msg = []
        data = os.environ['YOUDAO_COOKIES']
        for cookies in data.split('\n'):
            account = YouDao(cookies)
            msg.append(f"---账号: {account.uid}---")
            res = account.checkin()
            msg.append(res)
        return msg


if __name__ == '__main__':
    YouDao.start()
