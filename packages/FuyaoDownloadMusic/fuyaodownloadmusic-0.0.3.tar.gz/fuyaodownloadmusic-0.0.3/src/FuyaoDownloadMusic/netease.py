"""
encoding:   -*- coding: utf-8 -*-
@Time           :  2025/9/5 0:45
@Project_Name   :  spider
@Author         :  lhw
@File_Name      :  netease.py

功能描述

实现步骤

"""
import logging
import requests
import execjs
from FuyaoDownloadMusic import SONG_URL_PARAMS
from pathlib import Path

APIS = {
    # "search": "https://music.163.com/weapi/search/suggest/web",
    "search": "https://music.163.com/weapi/cloudsearch/pc",
    # "songDetail": "https://music.163.com/api/v3/song/detail",
    "songDetail": "https://music.163.com/weapi/song/enhance/player/url/v1",
}

current_path = Path(__file__).resolve().parent
ENCRYPT_JS_PATH = current_path / 'js' / 'NeteaseEncrypt.js'


def encrypt(func, data, logger: logging.Logger):
    # data = {
    #     "hlpretag": "<span class=\"s-fc7\">",
    #     "hlposttag": "</span>",
    #     "s": "知我",
    #     "type": "1",
    #     "offset": "0",
    #     "total": "true",
    #     "limit": "30",
    #     "csrf_token": ""
    # }
    # data = str(data)

    logger.info(f"函数：encrypt，调用者：{func}")

    logger.info("加密前：", data)

    with open(ENCRYPT_JS_PATH, "r", encoding="utf-8") as f:
        js_code = f.read()

    js_compile = execjs.compile(js_code)
    encrypted = js_compile.call("main", data)

    logger.info("加密后：", encrypted)

    return encrypted


class Netease:

    def __init__(
            self, logger: logging.Logger = logging.getLogger(),
            MUSIC_U="1eb9ce22024bb666e99b6743b2222f29ef64a9e88fda0fd5754714b900a5d70d993166e004087dd3b95085f6a85b059f5e9aba41e3f2646e3cebdbec0317df58c119e5"
            ):
        self.logger = logger

        self.logger.info("===网易云源==")

        self.searchApi = APIS["search"]
        self.songDetailApi = APIS["songDetail"]

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
            # "Cookie": "_iuqxldmzr_=32; _ntes_nnid=0ab2be8f90fa92dff74a3f463d32912a,1756282254881; _ntes_nuid=0ab2be8f90fa92dff74a3f463d32912a; NMTID=00O0cQZjOzPGuuhdkY3p9uMQwPZJnYAAAGY60u3sQ; WM_TID=OJFMmPHtNh1EAEQQUQKDhOieYdrPh%2Fg3; WEVNSM=1.0.0; WNMCID=jwjnud.1756294285387.01.0; sDeviceId=YD-WiXg3sBrPa5ER1RRFQOTxb3fJfRVjrHH; __snaker__id=Kq7aIfnHKHyCou8y; ntes_utid=tid._.Iu1Za%252BNo1%252BFAFlBQRBKX0ezfYLVUn7GG._.0; ntes_kaola_ad=1; WM_NI=dMI3uEM1JeznVEQ5kZuywqkaxrewpFEHWmpti0dQHu0YdtSfipaSiGlDz0k2Xajt92QSo4q%2FHSIKMGgl9IRA2KkWnXb%2Fq35rPgUztrVNY45H5FHan92ShizxtdQnjC6EbGc%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee91e75998b88c94ec80a3968ea7d84f838f8e86d66dbcbdb698e554a5939faeb62af0fea7c3b92aa89387d4f84f8fef8686f966969b9fd6ea52b7a7b992ea6bbcaeab98f34e8798998ef380abf0acb2cb7ff487ac95d26eabb0afb4ec4db09cb6d1ea3a9cbfa695bc3a938da1d5f4258c8d87acd04da5b4f7aad14bf295a5b8ed54a2f1bfd4b87a94b99b9bf77a969297d5b844f79a8882ed33f28da88af974b8bc9f8fe949f69baea8e237e2a3; __csrf=8fbdc94d0a4d108993f9708a65e1eae9; MUSIC_U=0000DBFE7A1E6BEDE3C194C815BAA090762E4C36C674FA73DDA775DA7052D4C2ED885A1B1F2DB07311E83CACF1F977B5628334E87D9A3B707014F120DFEAE1B437C7CB5B267A099377A1499B050C865A3E89EC81742D5DC0941308E93FF98689F347B3DDFF12A688E422735837120CABD7FF424C71E4704F50D487DE3BAE4E71FD12CE535702A58A256ECAD508FF12077C5C0B179941377C106865C991E95757EB96B3A647EC240AC2F8D12A88FEE0526526C4B8A7594F015F5258B19BFACA36FFC106DAD7688B708E3D8000ED38CDED36BE1A264FD7142F1E006A72C21FDE592E0A687A201163797929643262D116C6E4B8E104D053958F91D5B98F802F56F763743FFE4EAEF10FE20CA20E3F507513F082D040EFDECE8B4192F377231610C7290146551146EE027CB18E6E6CD043F26BE57B55E065C27D294DE60EC1334544AE84874F2CD7343612B2DF71BCB0677434472AAC95502C1489D8256A9F1AFA5DD8D653D97BAFA037F61453637DBA9ED440977D3A6470DA9CD7F1039365983FB9B62958CDF480563D9C3738E2E6F3E7A2405AAF90D0AC4B1F2C3F828EACAA5C7B43; JSESSIONID-WYYY=A8JJT%2F92TS4Mqy8lkEDSKyT479C16XM%5CB8%5Co2b6AKfy0kSEqN%2BkEZ1KdljXH1SFS9TYP4s81Ef61RGOUArB4wO8Y%2Fngy1X%2FY37uMwNCAMpY6QB4BQIDFoFc91NOgkw1fnV%2BuzR6%5CXZQ49XtpvEFYnH%2B%2BypH6nD7uXEnlOQeiUd7kry1v%3A1757042145239; gdxidpyhxdE=DNGvJlBEIQm45YdBpuqe%5CtjNnMKR6tKnNSkvWNINrzoTY%2Bh28Ton1mGcx3%2BWJZcBq79JcbWyy%2BuHmgem94m6gfL6IW9o2y%5C8UIL44n16DI7KWUNLErU%2Bnjz3c2%5C9B2xXA%2BpXpluI2Uhw57SCZC2vSAsorDC4o%2BNZmri5HdMzsKuk7%5Cnv%3A1757042349325",
            "Cookie": f"MUSIC_U={MUSIC_U};os=pc;appver=8.9.75;",
            "Referer": "https://music.163.com/",
            "host": "music.163.com",
            "origin": "https://music.163.com",

        }

        self.session = requests.Session()

    def search(self, searchParams: dict):
        """
        搜索歌曲
        Args:
            keyword:

        Returns:

        """
        self.logger.info("===搜索歌曲===")

        url = self.searchApi

        searchData = {
            # "hlpretag": "<span class=\"s-fc7\">",
            # "hlposttag": "</span>",
            "s": searchParams["keyword"],
            "type": "1",
            "offset": "0",
            "total": "true",
            "limit": searchParams["limit"],
            # "csrf_token": ""
        }

        encrypted_data = encrypt("Netease.search", str(searchData), self.logger)
        print(encrypted_data)

        data = {
            "params": encrypted_data["encText"],
            "encSecKey": encrypted_data["encSecKey"],
        }

        response = self.session.post(url=url, headers=self.headers, data=data)

        result = response.json()

        self.logger.info(f"搜索结果：{result}")

        songList = []
        for song in result["result"]["songs"]:
            songName = song["name"]
            songId = song["id"]
            songAuthors = ";".join([i["name"] for i in song["ar"]])
            songList.append({
                "songId": songId,
                "songName": songName,
                "songAuthors": songAuthors,
            })
            print(songId, songName, songAuthors)

        return songList

    def getSongUrl(self, songUrlParams: dict = SONG_URL_PARAMS["netease"]):
        """
        歌曲详情信息
        Args:
            songId:

        Returns:

        """
        self.logger.info(f"===获取歌曲url===")

        url = self.songDetailApi

        # params = {
        #     "csrf_token": "b3851062c68bbafb222fa64678eabf0d"
        # }

        songData = {
            "ids": f"[{songUrlParams['songId']}]",
            "level": "exhigh",
            "encodeType": "aac",
            # "csrf_token": "b3851062c68bbafb222fa64678eabf0d"
        }

        encrypted_data = encrypt("Netease.songDetail", str(songData), self.logger)

        data = {
            "params": encrypted_data["encText"],
            "encSecKey": encrypted_data["encSecKey"],
        }

        response = self.session.post(url=url, headers=self.headers, data=data)

        result = response.json()
        self.logger.info(f"歌曲详细信息: {result}")

        songUrl = result["data"][0]["url"]

        return songUrl

    def downloadSong(self, downloadMusicParams):
        """
        下载歌曲
        Args:
            songUrl:
            songSavePath:
            songName:

        Returns:

        """
        self.logger.info("===下载歌曲===")

        self.logger.info(f"歌曲名: {downloadMusicParams['songName']}; 歌曲源地址: {downloadMusicParams['songUrl']}")

        filePath = f"{downloadMusicParams['songSavePath']}/{downloadMusicParams['songName']}_{downloadMusicParams['songAuthors']}.mp3"
        with open(filePath, "wb") as f:
            f.write(self.session.get(url=downloadMusicParams['songUrl'], headers=self.headers).content)

        self.logger.info(
            f"{downloadMusicParams['songName']} 已经保存到 {filePath}")


if __name__ == '__main__':
    net = Netease(logging.getLogger())
    net.search({
        "s": "盲选",
        "limit": 30
    })
