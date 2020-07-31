# -*- coding: utf-8 -*-

import pyperclip
from fasttube import YouTube



if __name__=="__main__":
    video_url=input("video_address -> ")
    streams=YouTube(video_url)

    print("Available Quality:")
    for n, stm in enumerate(streams):
        print(f"\t{n}. {stm['quality']}")

    inp=int(input("chose a number -> "))

    pyperclip.copy(streams[inp]["url"])
    print("download link copied. go IDM -> Add Url")
