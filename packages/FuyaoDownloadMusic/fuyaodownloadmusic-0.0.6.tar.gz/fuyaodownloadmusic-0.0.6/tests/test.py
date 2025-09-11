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


def startDownload(musicSrc):
    print("===开始下载===")

    dm = DownloadMusic(musicSrcKey=musicSrc)

    # songTemplatePath = getConfig(SONG_TEMPLATE_PATH_KEY)
    # print("读取配置文件: 模板文件地址: %s", songTemplatePath)

    print("读取歌曲模板")
    with open("E:/song.txt", "r", encoding="utf-8") as f:
        songList = f.readlines()[1:]


    songInfoList = []

    for songs in songList:
        song = songs.split(",")
        songName = song[0]
        songAuthors = song[1]

        print("查询歌曲, 歌曲名: %s; 歌曲作者: %s", songName, songAuthors)
        searchResult = dm.search({
            "keyword": songName,
            "limit": 50,
        })
        print(searchResult)

        if len(searchResult) == 0:
            print("该音乐源未查询到歌曲")

        for r in searchResult:
            print(songAuthors, r["songAuthors"], songAuthors in r["songAuthors"])
            if songAuthors.strip() in [author.strip() for author in r["songAuthors"]]:
                songInfoList.append({
                    "songName": songName,
                    "songAuthors": "_".join(r["songAuthors"]),
                    "songId": r["songId"],
                })
                break

    print("所有歌曲查询完毕: %s", songInfoList)

    for songInfo in songInfoList:
        songUrl = dm.getSongUrl({
            "songId": songInfo["songId"]
        })

        print("下载歌曲: %s", songInfo["songName"])
        dm.downloadMusic({
            "songUrl": songUrl,
            "songName": songInfo["songName"],
            "songAuthors": songInfo["songAuthors"],
            "songSavePath": "E:/",
        })

    print("全部歌曲下载完毕")

if __name__ == '__main__':
    startDownload("netease")