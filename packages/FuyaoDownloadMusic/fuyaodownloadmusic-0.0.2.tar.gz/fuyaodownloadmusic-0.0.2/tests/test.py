"""
encoding:   -*- coding: utf-8 -*-
@Time           :  2025/9/10 20:41
@Project_Name   :  FuyaoDownloadMusic
@Author         :  lhw
@File_Name      :  test.py

功能描述

实现步骤

"""
from FuyaoDownloadMusic.download import DownloadMusic

dm = DownloadMusic(
    musicSrcKey="netease",  # 音乐源
    # cookieStr="...",  # 音乐平台的会员关键cookie
)

print(dm.search({
    "keyword": "知我",
    "limit": 30
}))