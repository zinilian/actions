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
        res = requests.post(url=url, cookies=cookies).json()
        print(res)
        if "error" not in res:
            checkin_response = requests.post(
                url="https://note.youdao.com/yws/mapi/user?method=checkin", cookies=cookies
            )
            print(checkin_response.json())
            unit_space = 1048576
            for i in range(3):
                ad_response = requests.post(
                    url="https://note.youdao.com/yws/mapi/user?method=adRandomPrompt", cookies=cookies
                )
                print(ad_response.text)
                ad_space += ad_response.json().get("space", 0) // unit_space
            sync_space = res.get("rewardSpace", 0) // unit_space
            checkin_space = checkin_response.json().get("space", 0) // unit_space
            space = sync_space + checkin_space + ad_space
            total_space = res.get('totalRewardSpace') // unit_space
            msg = [
                {
                    "name": "签到成功",
                    "value": f"+{space}M",
                },
                {
                    "name": "已获奖励",
                    "value": f"{total_space}M",
                },
                {
                    "name": "已连续签到",
                    "value": f"{res.get('continuousDays')}天"
                }
            ]
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
