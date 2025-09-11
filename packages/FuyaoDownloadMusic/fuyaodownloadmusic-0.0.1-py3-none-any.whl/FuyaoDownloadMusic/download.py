"""
encoding:   -*- coding: utf-8 -*-
@Time           :  2025/9/5 17:47
@Project_Name   :  FuyaoDownloadMusic
@Author         :  lhw
@File_Name      :  download.py

功能描述

实现步骤

"""
import logging
from src.FuyaoDownloadMusic.netease import Netease

MUSIC_SRC = {
    "netease": Netease,
}

SEARCH_PARAMS = {
    "netease": {
        "keyword": "知我",
        "limit": 30
    }
}


class DownloadMusic:

    def __init__(self, musicSrcKey: str, logger: logging.Logger = logging.getLogger(), cookieStr=None):
        if not cookieStr:
            self.musicSrc = MUSIC_SRC[musicSrcKey](logger)
        else:
            self.musicSrc = MUSIC_SRC[musicSrcKey](logger, cookieStr)

    def search(self, searchParams):
        return self.musicSrc.search(searchParams)

    def getSongUrl(self, songUrlParams):
        return self.musicSrc.getSongUrl(songUrlParams)

    def downloadMusic(self, downloadMusicParams):
        self.musicSrc.download(downloadMusicParams)


if __name__ == '__main__':
    dm = DownloadMusic("netease")
    # dm.search({
    #     "keyword": "此生不换",
    #     "limit": 50,
    # })

    songUrl = dm.getSongUrl({
        "songId": 1934168650,
    })
    print(songUrl)
